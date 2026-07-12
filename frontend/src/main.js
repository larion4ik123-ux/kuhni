import "./styles.css";

const basePath = import.meta.env.BASE_URL || "/";
const maxBotUrl = (import.meta.env.VITE_MAX_BOT_URL || "").trim();
const asset = (path) => `${basePath}${path}`.replace(/\/{2,}/g, "/");

const site = {
  brand: "Мебельный салон Интерьер",
  owner: "Артём Ермаков",
  contacts: {
    phone: "+7 (XXX) XXX-XX-XX",
    address: "—",
    region: "Людиново и ближайшие районы области",
    hours: "Пн-Пт: 9:00-18:00",
  },
  works: [
    ["work_4486", "Угловая кухня", "Современная кухня с зелёными нижними фасадами"],
    ["work_4494", "П-образная кухня", "Компактная П-образная кухня в зелёном цвете"],
    ["work_4492", "Линейная кухня", "Линейная кухня в спокойных серых оттенках"],
    ["work_4493", "Угловая кухня", "Серо-белая угловая кухня"],
    ["work_4495", "Угловая кухня", "Классическая белая угловая кухня"],
    ["work_4481", "Линейная кухня", "Светлая кухня с пеналами и встроенной техникой"],
    ["work_4491", "Угловая кухня", "Угловая кухня с древесной столешницей"],
    ["work_4489", "Угловая кухня", "Компактная угловая кухня со встроенной техникой"],
    ["work_4488", "Линейная кухня", "Зелёно-белая кухня с длинной рабочей зоной"],
  ].map(([image, title, alt]) => ({ image, title, alt })),
  styles: [
    ["Современные", "Чистые линии, удобное хранение и встроенная техника", "work_4486"],
    ["Неоклассика", "Светлая палитра и спокойные детали", "work_4493"],
    ["Модерн", "Выразительные сочетания цвета и фактуры", "work_4481"],
    ["Классика", "Тёплая атмосфера и фасады с характером", "work_4495"],
  ],
  process: [
    ["Знакомимся с задачей", "Обсуждаем помещение, стиль и ваши пожелания."],
    ["Выезжаю на замер", "Проверяю размеры, коммуникации и все важные привязки."],
    ["Готовим проект", "Подбираем материалы, наполнение и финальную конфигурацию."],
    ["Изготавливаем", "Собираем кухню в цехе под согласованный проект."],
    ["Доставляем", "Бережно привозим кухню на объект."],
    ["Устанавливаем", "Монтируем и сдаём готовую кухню."],
  ],
};

const icon = {
  max: `<img class="max-logo-icon" src="${asset("media/brand/max_icon.png")}" alt="" aria-hidden="true">`,
  arrow: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h12m-4.5-4.5L17 12l-4.5 4.5"/></svg>',
  left: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 6-6 6 6 6"/></svg>',
  right: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9.5 6 6 6-6 6"/></svg>',
  down: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
  menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>',
};

function kitchenImage(id, variant = "card") {
  return { webp: `media/kitchens_real/${id}_${variant}.webp`, jpg: `media/kitchens_real/${id}_${variant}.jpg` };
}

function picture({ webp, jpg, alt, className = "", loading = "eager" }) {
  return `<picture class="${className}"><source srcset="${asset(webp)}" type="image/webp"><img src="${asset(jpg)}" alt="${alt}" loading="${loading}" decoding="async"></picture>`;
}

function maxCta(label, source, className = "") {
  const content = `${icon.max}<span>${label}</span>${icon.arrow}`;
  return maxBotUrl
    ? `<a class="max-cta ${className}" href="${maxBotUrl}" data-cta="${source}">${content}</a>`
    : `<button class="max-cta ${className}" type="button" aria-disabled="true" data-cta="${source}">${content}</button>`;
}

const navItems = [["#works", "Работы"], ["#styles", "Варианты"], ["#about", "Обо мне"], ["#process", "Как работаю"], ["#faq", "Вопросы"], ["#contacts", "Контакты"]];
const nav = () => navItems.map(([href, label]) => `<a href="${href}">${label}</a>`).join("");

function header() {
  return `<header class="site-header" data-header>
    <a class="brand" href="#top" aria-label="${site.brand}">${picture({ webp: "media/brand/logo_interier_cropped_card.webp", jpg: "media/brand/logo_interier_cropped_card.jpg", alt: "Логотип мебельного салона Интерьер", className: "brand-logo" })}</a>
    <nav class="desktop-nav" aria-label="Основная навигация">${nav()}</nav>
    ${maxCta("Собрать кухню", "header", "header-cta")}
    <button class="menu-button" type="button" aria-label="Открыть меню" data-menu-toggle>${icon.menu}</button>
    <div class="mobile-panel" data-mobile-panel><button class="menu-close" type="button" aria-label="Закрыть меню" data-menu-close>${icon.close}</button><nav aria-label="Мобильная навигация">${nav()}</nav>${maxCta("Собрать кухню в MAX", "mobile_menu")}</div>
  </header>`;
}

function hero() {
  return `<section class="hero" id="top">
    <div class="hero-media">${picture({ webp: "media/kitchens_real/owner_in_workshop_hero.webp", jpg: "media/kitchens_real/owner_in_workshop_hero.jpg", alt: "Артём Ермаков в мебельном цехе", className: "hero-picture" })}</div>
    <div class="hero-overlay"></div>
    <div class="hero-copy"><p class="hero-kicker">Кухни и мебель на заказ</p><h1>Кухни на заказ<br>в городе Людиново</h1><p>Меня зовут Артём Ермаков. Я лично веду каждый проект: от первого разговора и замера до установки готовой кухни.</p><div class="hero-actions">${maxCta("Собрать кухню в MAX", "hero")}<a class="text-link" href="#works">Посмотреть работы ${icon.arrow}</a></div></div>
    <div class="owner-card"><strong>Артём Ермаков</strong><span>Основатель компании «Интерьер»</span></div>
  </section>`;
}

function proof() {
  return `<section class="proof section" aria-label="Преимущества"><div><strong>Более 10 лет</strong><span>изготавливаем кухни и мебель на заказ</span></div><div><strong>Сотни проектов</strong><span>в Людинове и ближайших районах</span></div><div><strong>Личный контроль</strong><span>за сроками и качеством каждого заказа</span></div></section>`;
}

function workCard(work, mode = "") {
  const image = kitchenImage(work.image, "card");
  const full = kitchenImage(work.image, "fullscreen");
  return `<article class="work-card ${mode}" data-lightbox="${asset(full.jpg)}" data-title="${work.title}"><button class="work-image" type="button" aria-label="Открыть: ${work.title}">${picture({ ...image, alt: work.alt, className: "work-picture" })}<span class="work-caption"><strong>${work.title}</strong><i>Открыть фото</i></span></button></article>`;
}

function works() {
  const featured = site.works.slice(0, 5);
  const extra = site.works.slice(5);
  return `<section class="section works" id="works"><div class="section-head"><div><p class="eyebrow">Реальные проекты</p><h2>Наши работы</h2></div><p>Кухни, которые уже собраны и установлены.</p></div><div class="work-stage"><div class="carousel-controls"><button type="button" data-carousel-prev aria-label="Предыдущая работа">${icon.left}</button><button type="button" data-carousel-next aria-label="Следующая работа">${icon.right}</button></div><div class="work-rail" data-work-carousel>${featured.map((work) => workCard(work, "rail-card")).join("")}</div></div><button class="reveal-works" type="button" data-more-works aria-expanded="false"><span>Показать все работы</span>${icon.down}</button><div class="works-extra" data-works-extra hidden>${extra.map((work) => workCard(work)).join("")}</div></section>`;
}

function styles() {
  return `<section class="section styles" id="styles"><div class="section-head"><div><p class="eyebrow">Для вашего дома</p><h2>Выберите направление</h2></div><p>Подберём стиль, который будет уместен именно в вашем интерьере.</p></div><div class="style-grid">${site.styles.map(([title, text, image]) => `<article class="style-card">${picture({ ...kitchenImage(image), alt: `${title} кухня`, className: "style-picture" })}<div><h3>${title}</h3><p>${text}</p></div></article>`).join("")}</div></section>`;
}

function botSection() {
  return `<section class="bot-section" id="bot"><div class="bot-inner"><div><p class="eyebrow">MAX-бот</p><h2>Соберите кухню своей мечты</h2><p>Ответьте на короткие вопросы, выберите материалы и добавьте фото помещения. Бот соберёт будущую кухню в понятный проект.</p>${maxCta("Открыть MAX-бот", "bot")}</div><ol><li><span>01</span><strong>Планировка и размеры</strong><p>Форма кухни, ширина, высота и площадь помещения.</p></li><li><span>02</span><strong>Стиль и детали</strong><p>Фасады, цвет, ручки, техника и ваши пожелания.</p></li><li><span>03</span><strong>Фото помещения</strong><p>Чтобы проект учитывал вашу реальную кухню.</p></li></ol></div></section>`;
}

function about() {
  return `<section class="section about" id="about"><div class="about-image">${picture({ ...kitchenImage("owner_in_showroom"), alt: "Артём Ермаков в салоне", className: "about-picture" })}</div><div class="about-copy"><p class="eyebrow">Обо мне</p><h2>Меня зовут Артём Ермаков</h2><p>Я основатель компании «Интерьер» в Людинове. Мы занимаемся изготовлением кухонь и мебели на заказ уже больше десяти лет.</p><p>Я лично участвую во всех этапах каждого заказа: от замера до установки. Когда есть один ответственный человек, проще договориться и быть уверенным в результате.</p><blockquote>«Я ручаюсь за качество каждого изделия, которое выходит из нашего цеха. Если вам что-то не понравится, я решу вопрос лично».</blockquote></div></section>`;
}

function process() {
  return `<section class="section process" id="process"><div class="section-head compact"><div><p class="eyebrow">Без лишней суеты</p><h2>Как я работаю</h2></div></div><ol class="process-grid">${site.process.map(([title, text], index) => `<li><span>${String(index + 1).padStart(2, "0")}</span><div><h3>${title}</h3><p>${text}</p></div></li>`).join("")}</ol></section>`;
}

function faq() {
  const items = [["Можно ли заказать кухню по фотографии?", "Да. По фотографии можно обсудить идею и планировку, а точные размеры и технические нюансы уточняем на замере."], ["Что можно сделать в MAX-боте?", "Выбрать форму и стиль кухни, отметить материалы и детали, добавить размеры и фото помещения."], ["Можно ли посмотреть материалы до заказа?", "Да. На встрече подберём фасады, столешницу, фурнитуру и оттенки под вашу задачу."], ["Делаете ли доставку и монтаж?", "Да. Изготавливаем кухню, доставляем на объект и устанавливаем."]];
  return `<section class="section faq" id="faq"><div class="section-head compact"><div><p class="eyebrow">Ответы на вопросы</p><h2>Важное перед началом</h2></div></div><div class="faq-list">${items.map(([q, a]) => `<details><summary>${q}</summary><p>${a}</p></details>`).join("")}</div></section>`;
}

function contacts() {
  return `<section class="section contacts" id="contacts"><div><p class="eyebrow">Контакты</p><h2>Обсудим вашу будущую кухню</h2><p>Работаю в Людинове и ближайших районах области.</p></div><dl><div><dt>Телефон</dt><dd>${site.contacts.phone}</dd></div><div><dt>Адрес</dt><dd>${site.contacts.address}</dd></div><div><dt>Регион работы</dt><dd>${site.contacts.region}</dd></div><div><dt>Время работы</dt><dd>${site.contacts.hours}</dd></div></dl></section>`;
}

function render() {
  document.querySelector("#app").innerHTML = `${header()}<main>${hero()}${proof()}${works()}${styles()}${botSection()}${about()}${process()}${faq()}${contacts()}</main><footer class="footer"><strong>${site.brand}</strong><span>Кухни и мебель на заказ в Людинове и ближайших районах.</span></footer><div class="mobile-max">${maxCta("Собрать кухню в MAX", "mobile_sticky")}</div><div class="lightbox" data-lightbox-modal hidden><button type="button" aria-label="Закрыть фото" data-lightbox-close>${icon.close}</button><img src="" alt=""><strong data-lightbox-title></strong></div>`;
}

function bindMenu() {
  const panel = document.querySelector("[data-mobile-panel]");
  const setOpen = (open) => { panel.classList.toggle("is-open", open); document.body.classList.toggle("has-menu", open); };
  document.querySelector("[data-menu-toggle]").addEventListener("click", () => setOpen(true));
  document.querySelector("[data-menu-close]").addEventListener("click", () => setOpen(false));
  panel.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setOpen(false)));
}

function bindGallery() {
  const rail = document.querySelector("[data-work-carousel]");
  const cardStep = () => (rail.querySelector(".work-card")?.getBoundingClientRect().width || 380) + 18;
  const move = (direction) => { const atEnd = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 24; rail.scrollTo({ left: direction > 0 && atEnd ? 0 : rail.scrollLeft + cardStep() * direction, behavior: "smooth" }); };
  document.querySelector("[data-carousel-prev]").addEventListener("click", () => move(-1));
  document.querySelector("[data-carousel-next]").addEventListener("click", () => move(1));
  if (!matchMedia("(prefers-reduced-motion: reduce)").matches) {
    let timer = setInterval(() => move(1), 5200);
    rail.addEventListener("pointerenter", () => { clearInterval(timer); timer = null; });
    rail.addEventListener("pointerleave", () => { if (!timer) timer = setInterval(() => move(1), 5200); });
  }
  const reveal = document.querySelector("[data-more-works]"); const extra = document.querySelector("[data-works-extra]");
  reveal.addEventListener("click", () => { const open = reveal.getAttribute("aria-expanded") === "true"; reveal.setAttribute("aria-expanded", String(!open)); reveal.querySelector("span").textContent = open ? "Показать все работы" : "Скрыть работы"; extra.hidden = open; });
}

function bindLightbox() {
  const modal = document.querySelector("[data-lightbox-modal]"); const image = modal.querySelector("img"); const title = modal.querySelector("[data-lightbox-title]");
  document.querySelectorAll("[data-lightbox]").forEach((card) => card.addEventListener("click", () => { image.src = card.dataset.lightbox; image.alt = card.dataset.title; title.textContent = card.dataset.title; modal.hidden = false; document.body.classList.add("has-lightbox"); }));
  const close = () => { modal.hidden = true; image.src = ""; document.body.classList.remove("has-lightbox"); };
  modal.querySelector("[data-lightbox-close]").addEventListener("click", close); modal.addEventListener("click", (event) => { if (event.target === modal) close(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
}

render(); bindMenu(); bindGallery(); bindLightbox();
