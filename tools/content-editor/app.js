"use strict";

const formRoot = document.querySelector("#form-content");
const status = document.querySelector("#save-status");
const saveButton = document.querySelector("#save-button");
const navButtons = [...document.querySelectorAll("[data-view]")];
let content = null;
let savedSnapshot = null;
let activeView = "site";
let dirty = false;

const get = (object, path) => path.reduce((value, key) => value?.[key], object);
const set = (object, path, value) => {
  const parent = get(object, path.slice(0, -1));
  parent[path.at(-1)] = value;
};

function note(text) {
  const help = document.createElement("span");
  help.className = "field-help";
  help.textContent = text;
  return help;
}

function card(title, description) {
  const section = document.createElement("section");
  section.className = "form-card";
  const heading = document.createElement("h2");
  heading.textContent = title;
  section.append(heading);
  if (description) section.append(note(description));
  formRoot.append(section);
  return section;
}

function field(parent, labelText, path, options = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = `field${options.wide ? " field--wide" : ""}`;
  const id = `field-${path.join("-")}-${crypto.randomUUID().slice(0, 6)}`;
  const label = document.createElement("label");
  label.htmlFor = id;
  label.textContent = labelText;
  const control = options.lines ? document.createElement("textarea") : document.createElement("input");
  control.id = id;
  control.name = path.join(".");
  control.readOnly = Boolean(options.readOnly);
  control.autocomplete = "off";
  control.value = options.lines
    ? (Array.isArray(get(content, path)) ? get(content, path).join("\n") : String(get(content, path) ?? ""))
    : String(get(content, path) ?? "");
  if (options.lines) {
    control.rows = options.rows || 4;
    control.spellcheck = true;
    control.addEventListener("input", () => {
      const current = get(content, path);
      const lines = control.value.split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
      set(content, path, Array.isArray(current) ? lines : control.value);
      markDirty();
    });
  } else {
    control.type = "text";
    if (options.type === "url") control.inputMode = "url";
    if (options.type === "url") control.inputMode = "url";
    control.maxLength = options.maxLength || 6000;
    control.addEventListener("input", () => {
      set(content, path, control.value);
      markDirty();
    });
  }
  wrapper.append(label, control);
  if (options.help) wrapper.append(note(options.help));
  parent.append(wrapper);
  return control;
}

function check(parent, labelText, path) {
  const wrapper = document.createElement("label");
  wrapper.className = "check-field";
  const control = document.createElement("input");
  control.type = "checkbox";
  control.checked = Boolean(get(content, path));
  control.addEventListener("change", () => {
    set(content, path, control.checked);
    markDirty();
  });
  const label = document.createElement("span");
  label.textContent = labelText;
  wrapper.append(control, label);
  parent.append(wrapper);
  return control;
}

function markDirty() {
  dirty = true;
  status.textContent = "Tienes cambios sin guardar.";
  status.dataset.state = "dirty";
}

function renderSite() {
  const identity = card("Identidad y navegación", "Estos datos se comparten entre las páginas del sitio.");
  field(identity, "Nombre para mostrar", ["site", "name"]);
  field(identity, "Dirección canónica del sitio", ["site", "siteUrl"], { type: "url", help: "Dirección HTTPS principal del sitio." });
  field(identity, "Idioma del sitio", ["site", "language"], { help: "Código de idioma, por ejemplo es." });
  field(identity, "Perfiles públicos (una URL por línea)", ["site", "sameAs"], { lines: true, rows: 3, help: "Se usan en la navegación y los enlaces de contacto." });

  const projectsPage = card("Presentación de Proyectos", "Introducción que aparece antes de las tarjetas y los filtros.");
  field(projectsPage, "Título", ["projectsPage", "title"]);
  field(projectsPage, "Introducción", ["projectsPage", "introduction"], { lines: true });
  field(projectsPage, "Contexto", ["projectsPage", "context"], { lines: true });

  const seo = card("Títulos para buscadores", "Edita los títulos y las descripciones sin cambiar rutas ni metadatos técnicos.");
  content.pages.forEach((page, index) => {
    field(seo, `${page.id}: título`, ["pages", index, "seo", "title"]);
    field(seo, `${page.id}: descripción`, ["pages", index, "seo", "description"], { lines: true, rows: 2 });
  });

  const notFound = card("Página no encontrada", "Texto de la página 404.");
  field(notFound, "Título", ["notFound", "title"]);
  field(notFound, "Descripción", ["notFound", "description"], { lines: true });
}

function renderHome() {
  const hero = card("Presentación principal", "El título es tu nombre. Usa el subtítulo para explicar por qué vale la pena seguir leyendo.");
  field(hero, "Nombre", ["home", "hero", "name"]);
  field(hero, "Subtítulo", ["home", "hero", "thesis"], { lines: true, rows: 2, help: "Una idea breve y propia. No agregues cifras que no puedas respaldar." });
  field(hero, "Párrafo de presentación", ["home", "hero", "introduction"], { lines: true, rows: 4 });
  field(hero, "Áreas de enfoque", ["home", "hero", "positioning"]);
  const actions = card("Acciones de la presentación", "Mantén cada destino como una ruta relativa o un enlace HTTPS.");
  content.home.hero.actions.forEach((item, index) => {
    field(actions, `Acción ${index + 1}: texto`, ["home", "hero", "actions", index, "label"]);
    field(actions, `Acción ${index + 1}: destino`, ["home", "hero", "actions", index, "href"], { type: "url" });
  });

  const signature = card("Forma de trabajo", "Cinco pasos con su explicación y una señal o evidencia asociada.");
  field(signature, "Antetítulo", ["home", "signature", "kicker"]);
  field(signature, "Título", ["home", "signature", "title"], { lines: true, rows: 2 });
  field(signature, "Introducción", ["home", "signature", "introduction"], { lines: true, rows: 2 });
  content.home.signature.stages.forEach((stage, index) => {
    const subgroup = document.createElement("div");
    subgroup.className = "nested-card";
    const label = document.createElement("h3");
    label.textContent = `${stage.number} · ${stage.title}`;
    subgroup.append(label);
    field(subgroup, "Nombre del paso", ["home", "signature", "stages", index, "title"]);
    field(subgroup, "Descripción", ["home", "signature", "stages", index, "description"], { lines: true, rows: 3 });
    field(subgroup, "Etiqueta de evidencia", ["home", "signature", "stages", index, "evidenceLabel"]);
    field(subgroup, "Evidencia", ["home", "signature", "stages", index, "evidence"], { lines: true, rows: 3 });
    signature.append(subgroup);
  });

  const selected = card("Tres proyectos destacados en Inicio", "Elige exactamente tres registros existentes. Sus tarjetas toman los datos resumidos de cada proyecto.");
  const selectedIds = new Set(content.home.selectedWork.projectIds);
  content.projects.forEach((project) => {
    const option = document.createElement("label");
    option.className = "check-field project-choice";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.checked = selectedIds.has(project.id);
    input.addEventListener("change", () => {
      if (input.checked && !selectedIds.has(project.id) && selectedIds.size >= 3) {
        input.checked = false;
        status.textContent = "Elige tres proyectos como máximo para la página de Inicio.";
        return;
      }
      if (input.checked) selectedIds.add(project.id); else selectedIds.delete(project.id);
      content.home.selectedWork.projectIds = content.projects.filter((item) => selectedIds.has(item.id)).map((item) => item.id);
      markDirty();
    });
    const text = document.createElement("span");
    text.textContent = project.title;
    option.append(input, text);
    selected.append(option);
  });
  field(selected, "Antetítulo", ["home", "selectedWork", "kicker"]);
  field(selected, "Título", ["home", "selectedWork", "title"], { lines: true, rows: 2 });

  const story = card("Trayectoria en Inicio", "Relato editorial separado de los datos formales del CV.");
  field(story, "Título", ["home", "careerStory", "heading"], { lines: true, rows: 2 });
  field(story, "Introducción", ["home", "careerStory", "introduction"], { lines: true, rows: 4 });
  content.home.careerStory.milestones.forEach((item, index) => {
    field(story, `Etapa ${index + 1}: nombre`, ["home", "careerStory", "milestones", index, "phase"]);
    field(story, `Etapa ${index + 1}: organización`, ["home", "careerStory", "milestones", index, "employer"]);
    field(story, `Etapa ${index + 1}: descripción`, ["home", "careerStory", "milestones", index, "description"], { lines: true, rows: 2 });
  });
  content.home.careerStory.notes.forEach((item, index) => {
    field(story, `Nota ${index + 1}: título`, ["home", "careerStory", "notes", index, "title"]);
    field(story, `Nota ${index + 1}: texto`, ["home", "careerStory", "notes", index, "body"], { lines: true, rows: 2 });
  });
  field(story, "Tema de exploración", ["home", "careerStory", "exploration", "title"]);
  field(story, "Antetítulo de exploración", ["home", "careerStory", "exploration", "kicker"]);
  field(story, "Descripción de exploración", ["home", "careerStory", "exploration", "description"], { lines: true, rows: 2 });

  const contact = card("Contacto y pie de página", "Enlaces visibles al final de Inicio.");
  field(contact, "Antetítulo", ["home", "contact", "eyebrow"]);
  field(contact, "Título", ["home", "contact", "title"]);
  field(contact, "Introducción", ["home", "contact", "introduction"], { lines: true, rows: 3 });
  content.home.contact.links.forEach((item, index) => {
    field(contact, `Enlace ${index + 1}: texto`, ["home", "contact", "links", index, "label"]);
    field(contact, `Enlace ${index + 1}: destino`, ["home", "contact", "links", index, "href"], { type: "url" });
  });
  field(contact, "Nombre del pie de página", ["home", "footer", "name"]);
  field(contact, "Descripción del pie de página", ["home", "footer", "tagline"]);
  field(contact, "Texto para volver arriba", ["home", "footer", "backToTop", "label"]);
}

function tagChoices(parent, project, projectPath) {
  const group = document.createElement("fieldset");
  group.className = "tag-select";
  const legend = document.createElement("legend");
  legend.textContent = "Temas del proyecto";
  group.append(legend);
  content.taxonomy.tags.forEach((tag) => {
    const option = document.createElement("label");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.checked = project.tags.includes(tag.id);
    input.addEventListener("change", () => {
      project.tags = content.taxonomy.tags.filter((item) => group.querySelector(`input[value="${CSS.escape(item.id)}"]`)?.checked).map((item) => item.id);
      markDirty();
    });
    input.value = tag.id;
    const text = document.createElement("span");
    text.textContent = tag.label;
    option.append(input, text);
    group.append(option);
  });
  parent.append(group);
}

function renderProjects() {
  const taxonomy = card("Temas para filtrar", "Las etiquetas son compartidas por los proyectos; conservá identificadores estables.");
  content.taxonomy.tags.forEach((tag, index) => {
    field(taxonomy, `Etiqueta ${index + 1}`, ["taxonomy", "tags", index, "label"]);
  });

  const heading = card("Experiencias y casos", "Puedes actualizar el contenido y las etiquetas. Los cuatro casos con ruta mantienen sus destinos actuales.");
  const addProject = document.createElement("button");
  addProject.type = "button";
  addProject.className = "secondary-button";
  addProject.textContent = "Agregar proyecto";
  addProject.addEventListener("click", () => {
    content.projects.push({ id: "nuevo-proyecto", title: "", group: "Otros proyectos", summary: "", situation: "", task: "", contribution: "", result: "", evidence: "", tags: [], featured: false, route: null });
    markDirty();
    render();
    formRoot.querySelectorAll("details").at(-1)?.querySelector("summary")?.focus();
  });
  heading.append(addProject);
  content.projects.forEach((project, index) => {
    const subgroup = document.createElement("details");
    subgroup.className = "project-editor";
    const summary = document.createElement("summary");
    summary.textContent = `${project.featured ? "Destacado · " : ""}${project.title}`;
    subgroup.append(summary);
    field(subgroup, "Identificador estable", ["projects", index, "id"], {
      readOnly: Boolean(project.route || content.home.selectedWork.projectIds.includes(project.id)),
      help: "Se conserva para proteger enlaces y selecciones; los registros nuevos admiten un identificador propio.",
    });
    field(subgroup, "Título", ["projects", index, "title"]);
    field(subgroup, "Grupo", ["projects", index, "group"]);
    field(subgroup, "Resumen", ["projects", index, "summary"], { lines: true, rows: 2 });
    field(subgroup, "Situación", ["projects", index, "situation"], { lines: true, rows: 2 });
    field(subgroup, "Tarea", ["projects", index, "task"], { lines: true, rows: 2 });
    field(subgroup, "Contribución", ["projects", index, "contribution"], { lines: true, rows: 2 });
    field(subgroup, "Resultado", ["projects", index, "result"], { lines: true, rows: 2 });
    field(subgroup, "Evidencia o alcance", ["projects", index, "evidence"], { lines: true, rows: 2 });
    const featured = check(subgroup, "Incluir entre los proyectos destacados de Proyectos", ["projects", index, "featured"]);
    featured.addEventListener("change", () => {
      if (content.projects.filter((item) => item.featured).length > 4) {
        featured.checked = false;
        project.featured = false;
        status.textContent = "Mantén cuatro proyectos destacados para que el sitio conserve su estructura.";
      }
    });
    tagChoices(subgroup, project, ["projects", index]);
    if (project.homeCard) {
      const homeCard = document.createElement("div");
      homeCard.className = "nested-card";
      const label = document.createElement("h3");
      label.textContent = "Tarjeta resumida de Inicio";
      homeCard.append(label);
      for (const key of ["title", "situation", "task", "contribution", "result"]) {
        field(homeCard, key === "title" ? "Título de tarjeta" : `Tarjeta: ${key}`, ["projects", index, "homeCard", key], { lines: key !== "title", rows: 2 });
      }
      subgroup.append(homeCard);
    }
    if (project.caseDetails) {
      const details = project.caseDetails;
      for (const key of ["hero", "context", "problem", "role", "outcome"]) {
        const block = details[key];
        const section = document.createElement("div");
        section.className = "nested-card";
        const label = document.createElement("h3");
        label.textContent = `Caso · ${key}`;
        section.append(label);
        for (const fieldName of Object.keys(block)) {
          if (typeof block[fieldName] === "string") field(section, fieldName, ["projects", index, "caseDetails", key, fieldName], { lines: fieldName !== "kicker", rows: 2 });
        }
        subgroup.append(section);
      }
      const approach = document.createElement("div");
      approach.className = "nested-card";
      const approachTitle = document.createElement("h3");
      approachTitle.textContent = "Caso · decisiones de abordaje (una por línea)";
      approach.append(approachTitle);
      field(approach, "Decisiones", ["projects", index, "caseDetails", "approach", "decisions"], { lines: true, rows: 5 });
      subgroup.append(approach);
      details.metrics.forEach((item, metricIndex) => {
        field(subgroup, `Métrica ${metricIndex + 1}: valor`, ["projects", index, "caseDetails", "metrics", metricIndex, "value"]);
        field(subgroup, `Métrica ${metricIndex + 1}: explicación`, ["projects", index, "caseDetails", "metrics", metricIndex, "label"]);
      });
    }
    if (!project.route && !content.home.selectedWork.projectIds.includes(project.id)) {
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "remove-button";
      remove.textContent = "Quitar este proyecto";
      remove.addEventListener("click", () => {
        if (!window.confirm(`¿Quieres quitar “${project.title || "este registro"}” de la lista? Para guardar, mantén los nueve registros del sitio.`)) return;
        content.projects.splice(index, 1);
        markDirty();
        render();
      });
      subgroup.append(remove);
    }
    heading.append(subgroup);
  });
  const callout = document.createElement("p");
  callout.className = "field-help project-count-note";
  callout.textContent = "La estructura actual requiere nueve registros, cuatro casos con ruta y cuatro proyectos destacados. Para reemplazar una experiencia, elimina primero una tarjeta secundaria y agrega su reemplazo antes de guardar.";
  heading.append(callout);
}

function renderCv() {
  const profile = card("Perfil profesional", "Datos que se muestran en la página del CV.");
  for (const key of ["profession", "location", "positioning", "summary", "workflow", "cvPdfUrl"]) {
    field(profile, ({ profession: "Profesión", location: "Ubicación", positioning: "Áreas de enfoque", summary: "Perfil", workflow: "Forma de trabajo", cvPdfUrl: "Enlace al PDF" })[key], ["profile", key], { lines: ["positioning", "summary", "workflow"].includes(key), type: key === "cvPdfUrl" ? "url" : "text", rows: 3 });
  }
  const education = card("Formación", "Mantén los datos tal como aparecen en el CV.");
  for (const key of ["degree", "institution", "year"]) field(education, ({ degree: "Título", institution: "Institución", year: "Año" })[key], ["education", key]);
  const languages = card("Idiomas", "Una fila por idioma.");
  content.languages.forEach((item, index) => {
    field(languages, `Idioma ${index + 1}`, ["languages", index, "language"]);
    field(languages, `Nivel ${index + 1}`, ["languages", index, "level"]);
  });
  const skills = card("Capacidades y herramientas", "Usa una línea por capacidad, herramienta o descripción.");
  content.skills.forEach((item, index) => {
    field(skills, `Área ${index + 1}`, ["skills", index, "area"]);
    field(skills, `Descripción ${index + 1}`, ["skills", index, "description"], { lines: true, rows: 2 });
    field(skills, `Capacidades ${index + 1}`, ["skills", index, "skills"], { lines: true, rows: 3 });
    field(skills, `Herramientas ${index + 1}`, ["skills", index, "tools"], { lines: true, rows: 3 });
  });
  const career = card("Experiencia profesional", "La trayectoria del CV mantiene cada empleador, período y evidencia por separado.");
  content.career.forEach((employer, index) => {
    const section = document.createElement("details");
    section.className = "project-editor";
    const summary = document.createElement("summary");
    summary.textContent = employer.employer;
    section.append(summary);
    field(section, "Organización", ["career", index, "employer"]);
    field(section, "Período", ["career", index, "period"]);
    if (employer.summary !== undefined) field(section, "Descripción", ["career", index, "summary"], { lines: true, rows: 2 });
    employer.roles.forEach((role, roleIndex) => {
      field(section, `Cargo ${roleIndex + 1}`, ["career", index, "roles", roleIndex, "title"]);
      field(section, `Período del cargo ${roleIndex + 1}`, ["career", index, "roles", roleIndex, "period"]);
      field(section, `Aportes del cargo ${roleIndex + 1} (una línea por punto)`, ["career", index, "roles", roleIndex, "bullets"], { lines: true, rows: 4 });
    });
    career.append(section);
  });
}

function render() {
  if (!content) return;
  formRoot.replaceChildren();
  ({ site: renderSite, home: renderHome, projects: renderProjects, cv: renderCv })[activeView]();
  formRoot.scrollIntoView({ block: "start", behavior: "smooth" });
}

navButtons.forEach((button) => button.addEventListener("click", () => {
  if (dirty && !window.confirm("Tienes cambios sin guardar. ¿Quieres cambiar de sección y descartarlos?")) return;
  if (dirty) content = structuredClone(savedSnapshot);
  activeView = button.dataset.view;
  dirty = false;
  status.textContent = "Los cambios aún no se guardaron.";
  navButtons.forEach((item) => {
    const selected = item === button;
    item.classList.toggle("is-active", selected);
    if (selected) item.setAttribute("aria-current", "page"); else item.removeAttribute("aria-current");
  });
  render();
}));

saveButton.addEventListener("click", async () => {
  saveButton.disabled = true;
  status.textContent = "Validando y reconstruyendo…";
  try {
    const response = await fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(content),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "No se pudo guardar el contenido.");
    dirty = false;
    savedSnapshot = structuredClone(content);
    status.dataset.state = "saved";
    status.textContent = result.message;
  } catch (error) {
    status.dataset.state = "error";
    status.textContent = error.message;
  } finally {
    saveButton.disabled = false;
  }
});

window.addEventListener("beforeunload", (event) => {
  if (!dirty) return;
  event.preventDefault();
  event.returnValue = "";
});

fetch("/api/content")
  .then((response) => {
    if (!response.ok) throw new Error("No se pudo cargar el contenido.");
    return response.json();
  })
  .then((data) => { content = data; savedSnapshot = structuredClone(data); render(); })
  .catch((error) => {
    formRoot.textContent = error.message;
    status.dataset.state = "error";
    status.textContent = "No se pudo abrir el contenido del sitio.";
  });
