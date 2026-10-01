"use strict";

const signature = document.querySelector("[data-signature]");
const signatureSteps = signature ? [...signature.querySelectorAll(".signature-step")] : [];
const signatureRoute = signature ? signature.querySelector(".signature-route") : null;
const tabsBreakpoint = window.matchMedia("(min-width: 1024px)");
let tabList = null;
let tabButtons = [];
let selectedIndex = Math.max(0, signatureSteps.findIndex((step) => step.open));
let desktopTabs = false;

function updateSignatureRoute(index) {
  if (!signatureRoute) return;
  signatureRoute.dataset.activeIndex = String(index);
  signatureRoute.querySelectorAll("[data-node]").forEach((node, nodeIndex) => {
    node.classList.toggle("is-complete", nodeIndex < index);
    node.classList.toggle("is-active", nodeIndex === index);
  });
  signatureRoute.querySelectorAll("[data-connection]").forEach((connection, connectionIndex) => {
    connection.classList.toggle("is-complete", connectionIndex < index);
    connection.classList.toggle("is-active", connectionIndex === index);
  });
}

function setSelected(index, moveFocus = false) {
  selectedIndex = (index + signatureSteps.length) % signatureSteps.length;
  signatureSteps.forEach((step, stepIndex) => {
    const selected = stepIndex === selectedIndex;
    step.hidden = desktopTabs && !selected;
    step.open = selected || (!desktopTabs && (stepIndex === selectedIndex || step.open));
    if (desktopTabs) {
      step.setAttribute("role", "tabpanel");
      step.setAttribute("aria-labelledby", tabButtons[stepIndex].id);
      step.tabIndex = selected ? 0 : -1;
      tabButtons[stepIndex].setAttribute("aria-selected", String(selected));
      tabButtons[stepIndex].tabIndex = selected ? 0 : -1;
    } else {
      step.removeAttribute("role");
      step.removeAttribute("aria-labelledby");
      step.removeAttribute("tabindex");
    }
  });
  updateSignatureRoute(selectedIndex);
  if (moveFocus && tabButtons[selectedIndex]) tabButtons[selectedIndex].focus();
}

function createTabList() {
  tabList = document.createElement("div");
  tabList.className = "signature-tabs";
  tabList.setAttribute("role", "tablist");
  tabList.setAttribute("aria-label", "Etapas de mi forma de trabajar");
  tabButtons = signatureSteps.map((step, index) => {
    const button = document.createElement("button");
    const summary = step.querySelector("summary");
    button.type = "button";
    button.id = `signature-tab-${index + 1}`;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", step.id);
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;
    button.innerHTML = `<span class="step-number">${String(index + 1).padStart(2, "0")}</span><span>${summary.querySelector("span:last-child").textContent}</span>`;
    button.addEventListener("click", () => setSelected(index));
    button.addEventListener("keydown", (event) => {
      let nextIndex = index;
      if (event.key === "ArrowRight") nextIndex += 1;
      else if (event.key === "ArrowLeft") nextIndex -= 1;
      else if (event.key === "Home") nextIndex = 0;
      else if (event.key === "End") nextIndex = signatureSteps.length - 1;
      else return;
      event.preventDefault();
      setSelected(nextIndex, true);
    });
    return button;
  });
  tabList.append(...tabButtons);
  const container = signature.querySelector(".signature-steps");
  if (signatureRoute) signatureRoute.after(tabList);
  else container.prepend(tabList);
}

function updateSignatureMode() {
  const focus = document.activeElement;
  const focusedTabIndex = tabButtons.indexOf(focus);
  const focusedSummaryIndex = signatureSteps.findIndex((step) => step.querySelector("summary") === focus);
  const shouldUseTabs = tabsBreakpoint.matches;

  if (shouldUseTabs && !desktopTabs) {
    if (!tabList) createTabList();
    desktopTabs = true;
    signatureSteps.forEach((step) => { step.querySelector("summary").tabIndex = -1; });
    setSelected(selectedIndex);
    if (focusedSummaryIndex >= 0) tabButtons[focusedSummaryIndex].focus();
  } else if (!shouldUseTabs && desktopTabs) {
    desktopTabs = false;
    signatureSteps.forEach((step) => {
      step.hidden = false;
      step.querySelector("summary").removeAttribute("tabindex");
    });
    setSelected(selectedIndex);
    if (focusedTabIndex >= 0) signatureSteps[focusedTabIndex].querySelector("summary").focus();
  }
}

try {
  if (signatureSteps.length === 5) {
    signatureSteps.forEach((step, index) => {
      if (!step.id) step.id = `signature-panel-${index + 1}`;
      step.addEventListener("toggle", () => {
        if (!desktopTabs && step.open) {
          selectedIndex = index;
          updateSignatureRoute(index);
        }
      });
    });
    updateSignatureMode();
    tabsBreakpoint.addEventListener("change", updateSignatureMode);
  }

  document.querySelectorAll('[data-action="print"]').forEach((control) => {
    control.addEventListener("click", () => window.print());
  });
  document.documentElement.classList.add("js");
} catch (error) {
  if (tabList) tabList.remove();
  signatureSteps.forEach((step) => {
    step.hidden = false;
    step.removeAttribute("role");
    step.removeAttribute("aria-labelledby");
    step.removeAttribute("tabindex");
    step.querySelector("summary").removeAttribute("tabindex");
  });
  document.documentElement.classList.remove("js");
}
