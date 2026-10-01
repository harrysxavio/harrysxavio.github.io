"use strict";

document.documentElement.classList.add("js");

document.querySelectorAll('[data-action="print"]').forEach((control) => {
  control.addEventListener("click", () => window.print());
});
