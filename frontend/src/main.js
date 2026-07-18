import "./styles.css";

const basePath = import.meta.env.BASE_URL || "/";
const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL ||
  (window.location.hostname.endsWith("github.io") ? "https://194-147-78-106.sslip.io" : "")
).replace(/\/$/, "");
let maxBotUrl = (import.meta.env.VITE_MAX_BOT_URL || "").trim();

const asset = (path = "") => {
  if (/^https?:\/\//.test(path) || path.startsWith("data:")) return path;
  return `${basePath}${path.replace(/^\/+/, "")}`.replace(/([^:]\/)\/{2,}/g, "$1");
};
const escapeHtml = (value = "") => String(value).replace(
  /[&<>"']/g,
  (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[character],
);
const phoneHref = (phone = "") => `+${phone.replace(/\D/g, "")}`;

const site = {
  brand: "Мебельный салон Интерьер",
  phone: "+7 (910) 543-47-04",
  yandexUrl: "https://yandex.ru/maps/org/interyer/196977992081/",
  blocks: {
    hero_eyebrow: { content: "Кухни и мебель на заказ" },
    hero_title: { content: "Кухни на заказ в Людинове" },
    hero_subtitle: { content: "Меня зовут Артём Ермаков. Лично отвечаю за каждый заказ: от замера до установки готовой кухни." },
    benefit_1: { title: "Кухни от 150 000 ₽", content: "Без лишних салонных наценок" },
    benefit_2: { title: "Более 10 лет опыта", content: "Сотни проектов в Людинове и области" },
    benefit_3: { title: "Гарантия качества", content: "За материалы, изготовление и установку отвечаю лично" },
    max_title: { content: "Соберите будущую кухню до замера" },
    max_text: { content: "Ответьте на короткие вопросы, добавьте размеры и фото помещения. Артём увидит задачу целиком и предложит подходящее решение." },
    works_title: { content: "Примеры работ" },
    works_text: { content: "Несколько кухонь, которые уже установлены у клиентов." },
    about_title: { content: "Я отвечаю за результат сам" },
    about_text: { content: "Меня зовут Артём Ермаков, я основатель компании «Интерьер» в Людинове. Больше 10 лет мы изготавливаем кухни и мебель на заказ, а я лично веду каждый проект от первого замера до установки." },
    about_quote: { content: "Я ручаюсь за качество каждого изделия, которое выходит из нашего цеха. Если что-то не понравится, я решу вопрос лично." },
    reviews_title: { content: "Нас рекомендуют" },
    contacts_title: { content: "Обсудим вашу кухню" },
    contacts_text: { content: "Людиново и ближайшие районы области." },
  },
  works: [
    ["work_4486", "Угловая кухня", "Современная угловая кухня с зелёными нижними фасадами"],
    ["work_4494", "П-образная кухня", "Компактная П-образная кухня в зелёном цвете"],
    ["work_4492", "Линейная кухня", "Линейная кухня в спокойных серых оттенках"],
    ["work_4495", "Светлая классическая кухня", "Светлая кухня с классическими фасадами"],
  ].map(([image, title, alt]) => ({ image, title, alt })),
  reviews: [
    ["Viking2092", "Отметили консультацию, сборку в срок и работу Артёма с Романом."],
    ["Лидия", "Понравились внимательное отношение, быстрая доставка и результат."],
    ["Каролина Махаммедова", "Отдельно отметила качество мебели и внимательную работу консультантов."],
    ["Елена Б.", "Отметила большой выбор, внимательный подход и своевременную доставку."],
    ["Оксана Садкевич", "Встроенный шкаф изготовили и установили быстро и качественно."],
    ["Кира Д.", "Помогли с эскизом кухни, материалами и цветом. Проект выполнили качественно и в срок."],
    ["Светлана Пономаренко", "Не первый раз приобретают здесь мебель. Доставку и сборку оценили на отлично."],
    ["Татьяна Морарь", "Отметила быструю доставку, квалифицированных сотрудников и хорошее соотношение цены и качества."],
  ].map(([author, text]) => ({ author, text, rating: 5 })),
};

const block = (key) => site.blocks[key] || {};
const icon = {
  max: `<span class="max-logo-mark" aria-hidden="true"><img src="${asset("media/brand/max_icon_card.webp")}" alt=""></span>`,
  arrow: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h12m-4.5-4.5L17 12l-4.5 4.5"/></svg>',
  menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>',
  previous: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg>',
  next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>',
};

function kitchenImage(id, variant = "card") {
  return { webp: `media/kitchens_real/${id}_${variant}.webp`, jpg: `media/kitchens_real/${id}_${variant}.jpg` };
}

function editableImage(key, fallback) {
  const item = block(key);
  return { webp: item.webp_url || fallback.webp, jpg: item.image_url || fallback.jpg };
}

function picture({ webp, jpg, alt, className = "", loading = "eager" }) {
  const source = webp ? `<source srcset="${asset(webp)}" type="image/webp">` : "";
  return `<picture class="${className}">${source}<img src="${asset(jpg)}" alt="${escapeHtml(alt)}" loading="${loading}" decoding="async"></picture>`;
}

function maxCta(label, source, className = "") {
  const content = `${icon.max}<span>${escapeHtml(label)}</span>${icon.arrow}`;
  return maxBotUrl
    ? `<a class="max-cta ${className}" href="${escapeHtml(maxBotUrl)}" data-cta="${source}">${content}</a>`
    : `<button class="max-cta ${className}" type="button" aria-disabled="true" data-cta="${source}">${content}</button>`;
}

const navItems = [["#works", "Работы"], ["#about", "Обо мне"], ["#reviews", "Отзывы"], ["#contacts", "Контакты"]];
const nav = () => navItems.map(([href, label]) => `<a href="${href}">${label}</a>`).join("");

function header() {
  return `<header class="site-header"><a class="brand" href="#top" aria-label="${site.brand}"><picture class="brand-picture"><source srcset="${asset("media/brand/logo_interier_cropped_card.webp")}" type="image/webp"><img class="brand-logo" src="${asset("media/brand/logo_interier_cropped_card.jpg")}" alt="Мебельный салон Интерьер"></picture></a><nav class="desktop-nav" aria-label="Основная навигация">${nav()}</nav>${maxCta("Перейти в MAX", "header", "header-cta")}<button class="menu-button" type="button" aria-label="Открыть меню" data-menu-toggle>${icon.menu}</button><div class="mobile-panel" data-mobile-panel><button class="menu-close" type="button" aria-label="Закрыть меню" data-menu-close>${icon.close}</button><nav aria-label="Мобильная навигация">${nav()}</nav>${maxCta("Перейти в MAX", "mobile_menu")}</div></header>`;
}

function hero() {
  const image = editableImage("hero_image", kitchenImage("owner_4993", "hero"));
  return `<section class="hero" id="top"><div class="hero-media">${picture({ ...image, alt: "Артём Ермаков", className: "hero-picture", loading: "eager" })}</div><div class="hero-shade"></div><div class="hero-copy"><p class="eyebrow">${escapeHtml(block("hero_eyebrow").content)}</p><h1>${escapeHtml(block("hero_title").content)}</h1><p>${escapeHtml(block("hero_subtitle").content)}</p><div class="hero-actions">${maxCta("Собрать кухню в MAX", "hero")}<a class="hero-phone" href="tel:${phoneHref(site.phone)}">${escapeHtml(site.phone)}</a></div></div></section>`;
}

function benefits() {
  return `<section class="benefits" aria-label="Преимущества">${[1, 2, 3].map((number) => { const item = block(`benefit_${number}`); return `<article><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.content)}</span></article>`; }).join("")}</section>`;
}

function maxStrip() {
  return `<section class="max-strip"><div><p class="eyebrow">MAX-бот</p><h2>${escapeHtml(block("max_title").content)}</h2><p>${escapeHtml(block("max_text").content)}</p></div>${maxCta("Перейти в MAX", "strip")}</section>`;
}

function workCard(work) {
  const image = work.image_url ? { webp: work.webp_url, jpg: work.image_url } : kitchenImage(work.image, "card");
  const full = work.image_url || asset(kitchenImage(work.image, "fullscreen").jpg);
  return `<article class="work-card" data-lightbox="${escapeHtml(full)}" data-title="${escapeHtml(work.title)}"><button type="button" aria-label="Открыть: ${escapeHtml(work.title)}">${picture({ ...image, alt: work.alt, className: "work-picture" })}<span>${escapeHtml(work.title)}</span></button></article>`;
}

function works() {
  return `<section class="section works" id="works"><div class="section-title"><p class="eyebrow">Реальные проекты</p><h2>${escapeHtml(block("works_title").content)}</h2><p>${escapeHtml(block("works_text").content)}</p></div><div class="work-grid">${site.works.map(workCard).join("")}</div></section>`;
}

function about() {
  const image = editableImage("about_image", kitchenImage("owner_in_workshop_v2", "hero"));
  return `<section class="about" id="about"><div class="about-photo">${picture({ ...image, alt: "Артём Ермаков в мебельном цехе", className: "about-picture" })}</div><div class="about-copy"><p class="eyebrow">Обо мне</p><h2>${escapeHtml(block("about_title").content)}</h2><p>${escapeHtml(block("about_text").content)}</p><blockquote>«${escapeHtml(block("about_quote").content)}»</blockquote><a class="phone-link" href="tel:${phoneHref(site.phone)}">${escapeHtml(site.phone)}</a></div></section>`;
}

function reviews() {
  if (!site.reviews.length) return "";
  return `<section class="reviews" id="reviews"><div class="section-title"><p class="eyebrow">Отзывы</p><h2>${escapeHtml(block("reviews_title").content)}</h2><a href="${escapeHtml(site.yandexUrl)}" target="_blank" rel="noreferrer">Отзывы на Яндекс Картах ${icon.arrow}</a></div><div class="review-carousel"><div class="review-grid" data-review-track>${site.reviews.map((review) => `<article><div><strong>${escapeHtml(review.author)}</strong><span aria-label="${review.rating} из 5">${"★".repeat(review.rating)}</span></div><p>${escapeHtml(review.text)}</p></article>`).join("")}</div><div class="review-controls" aria-label="Листать отзывы"><button type="button" aria-label="Предыдущие отзывы" data-review-previous>${icon.previous}</button><button type="button" aria-label="Следующие отзывы" data-review-next>${icon.next}</button></div></div></section>`;
}

function contacts() {
  return `<section class="contacts" id="contacts"><div><p class="eyebrow">Контакты</p><h2>${escapeHtml(block("contacts_title").content)}</h2><p>${escapeHtml(block("contacts_text").content)}</p></div><div class="contact-actions"><a href="tel:${phoneHref(site.phone)}">${escapeHtml(site.phone)}</a><a href="${escapeHtml(site.yandexUrl)}" target="_blank" rel="noreferrer">Адрес и отзывы на Яндекс Картах ${icon.arrow}</a></div>${maxCta("Перейти в MAX", "contacts")}</section>`;
}

function render() {
  document.querySelector("#app").innerHTML = `${header()}<main>${hero()}${benefits()}${maxStrip()}${works()}${about()}${reviews()}${contacts()}</main><footer><strong>${site.brand}</strong><span>Кухни и мебель на заказ в Людинове</span></footer><div class="lightbox" data-lightbox-modal hidden><button type="button" aria-label="Закрыть фото" data-lightbox-close>${icon.close}</button><img src="" alt=""><strong data-lightbox-title></strong></div>`;
}

function bindInteractions() {
  const panel = document.querySelector("[data-mobile-panel]");
  const setOpen = (open) => { panel.classList.toggle("is-open", open); document.body.classList.toggle("has-menu", open); };
  document.querySelector("[data-menu-toggle]").addEventListener("click", () => setOpen(true));
  document.querySelector("[data-menu-close]").addEventListener("click", () => setOpen(false));
  panel.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setOpen(false)));

  const modal = document.querySelector("[data-lightbox-modal]");
  const image = modal.querySelector("img");
  const title = modal.querySelector("[data-lightbox-title]");
  document.querySelectorAll("[data-lightbox]").forEach((card) => card.addEventListener("click", () => { image.src = card.dataset.lightbox; image.alt = card.dataset.title; title.textContent = card.dataset.title; modal.hidden = false; document.body.classList.add("has-lightbox"); }));
  const close = () => { modal.hidden = true; image.src = ""; document.body.classList.remove("has-lightbox"); };
  modal.querySelector("[data-lightbox-close]").addEventListener("click", close);
  modal.addEventListener("click", (event) => { if (event.target === modal) close(); });

  const track = document.querySelector("[data-review-track]");
  if (track) {
    const scrollReviews = (direction) => { const card = track.querySelector("article"); const gap = parseFloat(getComputedStyle(track).columnGap) || 16; track.scrollBy({ left: direction * ((card?.getBoundingClientRect().width || track.clientWidth) + gap), behavior: "smooth" }); };
    document.querySelector("[data-review-previous]").addEventListener("click", () => scrollReviews(-1));
    document.querySelector("[data-review-next]").addEventListener("click", () => scrollReviews(1));
  }
}

function mount() { render(); bindInteractions(); }

async function loadEditableContent() {
  try {
    const response = await fetch(`${apiBaseUrl}/api/site-content`, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Content API: ${response.status}`);
    const data = await response.json();
    site.blocks = { ...site.blocks, ...data.blocks };
    site.phone = data.contacts?.phone || site.phone;
    site.yandexUrl = data.contacts?.yandex_maps_url || site.yandexUrl;
    maxBotUrl = data.max_bot_url || data.contacts?.max_url || maxBotUrl;
    if (data.gallery?.length) site.works = data.gallery.filter((item) => item.image_url).map((item) => ({ image_url: item.image_url, webp_url: item.webp_url, title: item.caption || "Кухня на заказ", alt: item.alt_text || item.caption || "Кухня на заказ" }));
    if (data.reviews?.length) site.reviews = data.reviews.map((item) => ({ author: item.author_name, text: item.text, rating: item.rating }));
    mount();
  } catch (error) {
    console.info("Используется встроенная версия контента", error);
  }
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") document.querySelector("[data-lightbox-close]")?.click();
});

mount();
loadEditableContent();
