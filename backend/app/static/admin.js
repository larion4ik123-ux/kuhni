const csrf = document.querySelector('meta[name="csrf-token"]').content;
const state = { data: null, editor: null };
const dialog = document.querySelector("[data-editor]");
const fields = document.querySelector("[data-dialog-fields]");
const escapeHtml = (value = "") => String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { "X-CSRF-Token": csrf, ...(options.headers || {}) } });
  if (response.status === 401) { window.location.href = "/admin/login"; throw new Error("Сессия завершена"); }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || "Не удалось сохранить изменения");
  return payload;
}

function toast(message) {
  const node = document.querySelector("[data-toast]"); node.textContent = message; node.hidden = false;
  window.setTimeout(() => { node.hidden = true; }, 2600);
}

function blockCard(item) {
  return `<article class="content-card">${item.image_url ? `<img src="${escapeHtml(item.image_url)}" alt="">` : ""}<span class="card-meta">${escapeHtml(item.key)}</span><h3>${escapeHtml(item.title || item.key)}</h3><p>${escapeHtml(item.content || "Текст не заполнен")}</p><div class="card-actions"><button data-edit-block="${escapeHtml(item.key)}">Редактировать</button></div></article>`;
}
function galleryCard(item) {
  return `<article class="content-card">${item.image_url ? `<img src="${escapeHtml(item.image_url)}" alt="">` : ""}<span class="card-meta">${escapeHtml(item.layout || "работа")}</span><h3>${escapeHtml(item.caption || "Без подписи")}</h3><p>${escapeHtml(item.alt_text || "Описание не заполнено")}</p><div class="card-actions"><button data-edit-gallery="${item.id}">Редактировать</button><button class="danger" data-delete-gallery="${item.id}">Удалить</button></div></article>`;
}
function reviewCard(item) {
  return `<article class="content-card"><span class="card-meta">${"★".repeat(item.rating)}</span><h3>${escapeHtml(item.author_name)}</h3><p>${escapeHtml(item.text)}</p><div class="card-actions"><button data-edit-review="${item.id}">Редактировать</button><button class="danger" data-delete-review="${item.id}">Удалить</button></div></article>`;
}

function render() {
  document.querySelector("[data-block-list]").innerHTML = state.data.blocks.map(blockCard).join("");
  document.querySelector("[data-gallery-list]").innerHTML = state.data.gallery.map(galleryCard).join("") || "<p>Работ пока нет.</p>";
  document.querySelector("[data-review-list]").innerHTML = state.data.reviews.map(reviewCard).join("") || "<p>Отзывов пока нет.</p>";
}

async function refresh() { state.data = await api("/api/admin/content"); render(); }
const input = (name, label, value = "", type = "text") => `<label>${label}<input type="${type}" name="${name}" value="${escapeHtml(value ?? "")}"></label>`;
const textarea = (name, label, value = "") => `<label>${label}<textarea name="${name}">${escapeHtml(value ?? "")}</textarea></label>`;
const visible = (checked = true) => `<label class="check-field"><input type="checkbox" name="visible" ${checked ? "checked" : ""}>Показывать на сайте</label>`;
const fileField = (url) => `${url ? `<img class="image-preview" src="${escapeHtml(url)}" alt="Текущее изображение">` : ""}<label>Новое изображение<input type="file" name="file" accept="image/jpeg,image/png,image/webp"></label>`;

function openEditor(kind, item = {}) {
  state.editor = { kind, item };
  const isNew = !item.id && kind !== "block";
  document.querySelector("[data-dialog-kind]").textContent = kind === "block" ? "Блок сайта" : kind === "gallery" ? "Наша работа" : "Отзыв";
  document.querySelector("[data-dialog-title]").textContent = isNew ? "Добавить" : `Редактировать ${item.title || item.caption || item.author_name || ""}`;
  if (kind === "block") fields.innerHTML = `${fileField(item.image_url)}${input("title", "Название в админке", item.title)}${textarea("content", "Текст блока", item.content)}${visible(item.visible)}`;
  if (kind === "gallery") fields.innerHTML = `${fileField(item.image_url)}${input("caption", "Подпись", item.caption)}${textarea("alt_text", "Описание фотографии", item.alt_text)}${input("layout", "Тип кухни", item.layout)}${input("display_order", "Порядок", item.display_order || 0, "number")}${visible(item.visible ?? true)}`;
  if (kind === "review") fields.innerHTML = `${input("author_name", "Имя автора", item.author_name)}${textarea("text", "Текст отзыва", item.text)}${input("rating", "Оценка от 1 до 5", item.rating || 5, "number")}${input("source_url", "Ссылка на источник", item.source_url)}${input("display_order", "Порядок", item.display_order || 0, "number")}${visible(item.visible ?? true)}`;
  dialog.showModal();
}

async function save(event) {
  event.preventDefault();
  const { kind, item } = state.editor; const form = new FormData(document.querySelector("[data-editor-form]"));
  try {
    if (kind === "block") {
      await api(`/api/admin/blocks/${item.key}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: form.get("title"), content: form.get("content"), visible: form.get("visible") === "on" }) });
      if (form.get("file")?.size) { const upload = new FormData(); upload.append("file", form.get("file")); await api(`/api/admin/blocks/${item.key}/image`, { method: "POST", body: upload }); }
    }
    if (kind === "gallery" && item.id) {
      await api(`/api/admin/gallery/${item.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ caption: form.get("caption"), alt_text: form.get("alt_text"), layout: form.get("layout"), display_order: Number(form.get("display_order")) || 0, visible: form.get("visible") === "on" }) });
      if (form.get("file")?.size) { const upload = new FormData(); upload.append("file", form.get("file")); await api(`/api/admin/gallery/${item.id}/image`, { method: "POST", body: upload }); }
    } else if (kind === "gallery") {
      if (!form.get("file")?.size) throw new Error("Выберите фотографию работы");
      await api("/api/admin/gallery", { method: "POST", body: form });
    }
    if (kind === "review") {
      const payload = { author_name: form.get("author_name"), text: form.get("text"), rating: Number(form.get("rating")) || 5, source_url: form.get("source_url") || null, display_order: Number(form.get("display_order")) || 0, visible: form.get("visible") === "on" };
      await api(item.id ? `/api/admin/reviews/${item.id}` : "/api/admin/reviews", { method: item.id ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    }
    dialog.close(); await refresh(); toast("Изменения сохранены");
  } catch (error) { toast(error.message); }
}

document.querySelectorAll("[data-tab]").forEach((button) => button.addEventListener("click", () => {
  document.querySelectorAll("[data-tab]").forEach((item) => item.classList.toggle("is-active", item === button));
  document.querySelectorAll("[data-panel]").forEach((panel) => { panel.hidden = panel.dataset.panel !== button.dataset.tab; });
}));
document.addEventListener("click", async (event) => {
  const block = event.target.closest("[data-edit-block]"); if (block) openEditor("block", state.data.blocks.find((item) => item.key === block.dataset.editBlock));
  const gallery = event.target.closest("[data-edit-gallery]"); if (gallery) openEditor("gallery", state.data.gallery.find((item) => item.id === Number(gallery.dataset.editGallery)));
  const review = event.target.closest("[data-edit-review]"); if (review) openEditor("review", state.data.reviews.find((item) => item.id === Number(review.dataset.editReview)));
  if (event.target.closest("[data-add-gallery]")) openEditor("gallery", {});
  if (event.target.closest("[data-add-review]")) openEditor("review", {});
  const deleteGallery = event.target.closest("[data-delete-gallery]"); if (deleteGallery && confirm("Удалить эту работу с сайта?")) { await api(`/api/admin/gallery/${deleteGallery.dataset.deleteGallery}`, { method: "DELETE" }); await refresh(); }
  const deleteReview = event.target.closest("[data-delete-review]"); if (deleteReview && confirm("Удалить этот отзыв?")) { await api(`/api/admin/reviews/${deleteReview.dataset.deleteReview}`, { method: "DELETE" }); await refresh(); }
});
document.querySelector("[data-save]").addEventListener("click", save);
refresh().catch((error) => toast(error.message));
