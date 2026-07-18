import "./styles.css";

const basePath = import.meta.env.BASE_URL || "/";
const maxBotUrl = (import.meta.env.VITE_MAX_BOT_URL || "").trim();
const asset = (path) => `${basePath}${path}`.replace(/\/{2,}/g, "/");

const site = {
  brand: "Мебельный салон Интерьер",
  owner: "Артём Ермаков",
  phone: "+7 (910) 543-47-04",
  phoneHref: "+79105434704",
  yandexUrl: "https://yandex.ru/maps/org/interyer/196977992081/",
  works: [
    ["work_4486", "Угловая кухня", "Современная кухня с зелёными нижними фасадами"],
    ["work_4494", "П-образная кухня", "Компактная П-образная кухня в зелёном цвете"],
    ["work_4492", "Линейная кухня", "Линейная кухня в спокойных серых оттенках"],
    ["work_4495", "Классическая кухня", "Светлая кухня с классическими фасадами"],
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
    ["Ольга Б.", "Понравились широкий ассортимент и внимательные сотрудники, которые помогают с выбором."],
    ["Екатерина", "Заказывает мебель в «Интерьере» не первый год и отмечает качество и скорость работы."],
    ["Марина Д.", "Отметила качество мебели, большой ассортимент и компетентных сотрудников."],
    ["Галина", "Понравились большой выбор мебели и расцветок, а также отзывчивые продавцы."],
  ],
};

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

function picture({ webp, jpg, alt, className = "", loading = "lazy" }) {
  return `<picture class="${className}"><source srcset="${asset(webp)}" type="image/webp"><img src="${asset(jpg)}" alt="${alt}" loading="${loading}" decoding="async"></picture>`;
}

function maxCta(label, source, className = "") {
  const content = `${icon.max}<span>${label}</span>${icon.arrow}`;
  return maxBotUrl
    ? `<a class="max-cta ${className}" href="${maxBotUrl}" data-cta="${source}">${content}</a>`
    : `<button class="max-cta ${className}" type="button" aria-disabled="true" data-cta="${source}">${content}</button>`;
}

const navItems = [["#works", "Работы"], ["#about", "Обо мне"], ["#reviews", "Отзывы"], ["#contacts", "Контакты"]];
const nav = () => navItems.map(([href, label]) => `<a href="${href}">${label}</a>`).join("");

function header() {
  return `<header class="site-header"><a class="brand" href="#top" aria-label="${site.brand}"><picture class="brand-picture"><source srcset="${asset("media/brand/logo_interier_cropped_card.webp")}" type="image/webp"><img class="brand-logo" src="${asset("media/brand/logo_interier_cropped_card.jpg")}" alt="Мебельный салон Интерьер"></picture></a><nav class="desktop-nav" aria-label="Основная навигация">${nav()}</nav>${maxCta("Перейти в MAX", "header", "header-cta")}<button class="menu-button" type="button" aria-label="Открыть меню" data-menu-toggle>${icon.menu}</button><div class="mobile-panel" data-mobile-panel><button class="menu-close" type="button" aria-label="Закрыть меню" data-menu-close>${icon.close}</button><nav aria-label="Мобильная навигация">${nav()}</nav>${maxCta("Перейти в MAX", "mobile_menu")}</div></header>`;
}

function hero() {
  return `<section class="hero" id="top"><div class="hero-media">${picture({ ...kitchenImage("owner_4993", "hero"), alt: "Артём Ермаков в салоне Интерьер", className: "hero-picture", loading: "eager" })}</div><div class="hero-shade"></div><div class="hero-copy"><p class="eyebrow">Кухни и мебель на заказ</p><h1>Кухни на заказ<br>в Людинове</h1><p>Меня зовут Артём Ермаков. Лично отвечаю за каждый заказ: от замера до установки готовой кухни.</p><div class="hero-actions">${maxCta("Рассчитать кухню в MAX", "hero")}<a class="hero-phone" href="tel:${site.phoneHref}">${site.phone}</a></div></div></section>`;
}

function benefits() {
  return `<section class="benefits" aria-label="Преимущества"><article><strong>Кухни от 150 000 ₽</strong><span>Без лишних салонных наценок</span></article><article><strong>Более 10 лет опыта</strong><span>Сотни проектов в Людинове и области</span></article><article><strong>Гарантия качества</strong><span>За материалы, изготовление и установку отвечаю лично</span></article></section>`;
}

function maxStrip() {
  return `<section class="max-strip"><div><p class="eyebrow">MAX-бот</p><h2>Соберите будущую кухню до замера</h2><p>Ответьте на короткие вопросы, добавьте размеры и фото помещения. Артём увидит задачу целиком и предложит подходящее решение.</p></div>${maxCta("Перейти в MAX", "strip")}</section>`;
}

function workCard(work) {
  const image = kitchenImage(work.image, "card");
  const full = kitchenImage(work.image, "fullscreen");
  return `<article class="work-card" data-lightbox="${asset(full.jpg)}" data-title="${work.title}"><button type="button" aria-label="Открыть: ${work.title}">${picture({ ...image, alt: work.alt, className: "work-picture" })}<span>${work.title}</span></button></article>`;
}

function works() {
  return `<section class="section works" id="works"><div class="section-title"><p class="eyebrow">Реальные проекты</p><h2>Примеры работ</h2><p>Несколько кухонь, которые уже установлены у клиентов.</p></div><div class="work-grid">${site.works.map(workCard).join("")}</div></section>`;
}

function about() {
  return `<section class="about" id="about"><div class="about-photo">${picture({ ...kitchenImage("owner_4993", "hero"), alt: "Артём Ермаков, основатель компании Интерьер", className: "about-picture" })}</div><div class="about-copy"><p class="eyebrow">Личный подход</p><h2>Я отвечаю за результат сам</h2><p>Я основатель компании «Интерьер». Беру проект в работу лично: приезжаю на замер, контролирую изготовление и участвую в установке.</p><blockquote>«Я ручаюсь за качество каждого изделия, которое выходит из нашего цеха. Если что-то не понравится, я решу вопрос лично».</blockquote><a class="phone-link" href="tel:${site.phoneHref}">${site.phone}</a></div></section>`;
}

function reviews() {
  return `<section class="reviews" id="reviews"><div class="section-title"><p class="eyebrow">Отзывы</p><h2>Нас рекомендуют</h2><a href="${site.yandexUrl}" target="_blank" rel="noreferrer">Отзывы на Яндекс Картах ${icon.arrow}</a></div><div class="review-carousel"><div class="review-grid" data-review-track>${site.reviews.map(([author, text]) => `<article><div><strong>${author}</strong><span aria-label="5 из 5">★★★★★</span></div><p>${text}</p></article>`).join("")}</div><div class="review-controls" aria-label="Листать отзывы"><button type="button" aria-label="Предыдущие отзывы" data-review-previous>${icon.previous}</button><button type="button" aria-label="Следующие отзывы" data-review-next>${icon.next}</button></div></div></section>`;
}

function contacts() {
  return `<section class="contacts" id="contacts"><div><p class="eyebrow">Контакты</p><h2>Обсудим вашу кухню</h2><p>Людиново и ближайшие районы области.</p></div><div class="contact-actions"><a href="tel:${site.phoneHref}">${site.phone}</a><a href="${site.yandexUrl}" target="_blank" rel="noreferrer">Адрес и отзывы на Яндекс Картах ${icon.arrow}</a></div>${maxCta("Перейти в MAX", "contacts")}</section>`;
}

function render() {
  document.querySelector("#app").innerHTML = `${header()}<main>${hero()}${benefits()}${maxStrip()}${works()}${about()}${reviews()}${contacts()}</main><footer><strong>${site.brand}</strong><span>Кухни и мебель на заказ в Людинове</span></footer><div class="lightbox" data-lightbox-modal hidden><button type="button" aria-label="Закрыть фото" data-lightbox-close>${icon.close}</button><img src="" alt=""><strong data-lightbox-title></strong></div>`;
}

function bindMenu() {
  const panel = document.querySelector("[data-mobile-panel]");
  const setOpen = (open) => { panel.classList.toggle("is-open", open); document.body.classList.toggle("has-menu", open); };
  document.querySelector("[data-menu-toggle]").addEventListener("click", () => setOpen(true));
  document.querySelector("[data-menu-close]").addEventListener("click", () => setOpen(false));
  panel.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setOpen(false)));
}

function bindLightbox() {
  const modal = document.querySelector("[data-lightbox-modal]"); const image = modal.querySelector("img"); const title = modal.querySelector("[data-lightbox-title]");
  document.querySelectorAll("[data-lightbox]").forEach((card) => card.addEventListener("click", () => { image.src = card.dataset.lightbox; image.alt = card.dataset.title; title.textContent = card.dataset.title; modal.hidden = false; document.body.classList.add("has-lightbox"); }));
  const close = () => { modal.hidden = true; image.src = ""; document.body.classList.remove("has-lightbox"); };
  modal.querySelector("[data-lightbox-close]").addEventListener("click", close); modal.addEventListener("click", (event) => { if (event.target === modal) close(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
}

function bindReviews() {
  const track = document.querySelector("[data-review-track]");
  const scrollReviews = (direction) => {
    const card = track.querySelector("article");
    const gap = parseFloat(getComputedStyle(track).columnGap) || 16;
    track.scrollBy({ left: direction * ((card?.getBoundingClientRect().width || track.clientWidth) + gap), behavior: "smooth" });
  };
  document.querySelector("[data-review-previous]").addEventListener("click", () => scrollReviews(-1));
  document.querySelector("[data-review-next]").addEventListener("click", () => scrollReviews(1));
}

render(); bindMenu(); bindLightbox(); bindReviews();
