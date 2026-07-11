import "./styles.css";

const basePath = import.meta.env.BASE_URL || "/";
const asset = (path) => `${basePath}${path}`.replace(/\/{2,}/g, "/");

const site = {
  brand: {
    name: "Мебельный салон Интерьер",
    logo: {
      webp: "media/brand/logo_interier_cropped_card.webp",
      jpg: "media/brand/logo_interier_cropped_card.jpg",
      alt: "Логотип мебельного салона Интерьер",
    },
  },
  owner: {
    name: "Артём Ермаков",
    role: "основатель компании «Интерьер»",
  },
  contacts: {
    phone: "+7 (XXX) XXX-XX-XX",
    address: "—",
    region: "Людиново и ближайшие районы области",
    hours: "Пн-Пт: 9:00-18:00",
  },
  hero: {
    title: "Кухни на заказ в городе Людиново",
    text: "Меня зовут Артём Ермаков. Я основатель компании «Интерьер» и лично участвую в каждом проекте: от первого разговора и замера до установки кухни.",
    image: {
      webp: "media/kitchens_real/owner_in_workshop_hero.webp",
      jpg: "media/kitchens_real/owner_in_workshop_hero.jpg",
      alt: "Артём Ермаков в мебельном цехе",
    },
  },
  advantages: [
    ["Более 10 лет", "изготавливаем кухни и мебель на заказ"],
    ["Лично отвечаю", "за замер, сроки и качество проекта"],
    ["Людиново и округ", "работаем по городу и ближайшим районам"],
  ],
  generatorSteps: [
    ["01", "Расскажите о кухне", "Выберите форму, стиль и то, что для вас важно."],
    ["02", "Добавьте фото помещения", "Так легче понять планировку и предложить подходящее решение."],
    ["03", "Получите идею и оставьте заявку", "MAX-бот соберёт пожелания, а Артём свяжется, чтобы обсудить проект."],
  ],
  gallery: [
    ["work_4486", "Угловая кухня с зелёным акцентом", "Угловая", "Угловая кухня с зелёными нижними фасадами"],
    ["work_4494", "П-образная кухня в зелёном цвете", "П-образная", "П-образная зелёная кухня в компактном помещении"],
    ["work_4492", "Компактная линейная кухня", "Линейная", "Компактная линейная кухня в серых оттенках"],
    ["work_4493", "Серо-белая угловая кухня", "Угловая", "Серо-белая угловая кухня"],
    ["work_4495", "Классическая угловая кухня", "Угловая", "Классическая белая угловая кухня"],
    ["work_4481", "Светлая кухня с пеналами", "Линейная", "Светлая кухня с пеналами и встроенной техникой"],
    ["work_4491", "Угловая кухня с древесной столешницей", "Угловая", "Угловая кухня в графитовых и древесных оттенках"],
    ["work_4489", "Угловая кухня со встроенной техникой", "Угловая", "Компактная угловая кухня со встроенной техникой"],
    ["work_4488", "Зелёно-белая кухня с длинной рабочей зоной", "Линейная", "Кухня с зелёными фасадами и светлой столешницей"],
  ].map(([image, title, type, alt]) => ({ image, title, type, alt })),
  styles: [
    {
      title: "Современный",
      text: "Чёткие линии, спокойные фасады, встроенная техника и удобные зоны хранения.",
      image: "work_4486",
      alt: "Современная угловая кухня",
    },
    {
      title: "Неоклассика",
      text: "Мягкая геометрия, светлые оттенки и детали, которые делают интерьер теплее.",
      image: "work_4493",
      alt: "Кухня в стиле неоклассика",
    },
    {
      title: "Модерн",
      text: "Выразительные сочетания цвета и фактуры для интерьера с характером.",
      image: "work_4481",
      alt: "Кухня в стиле модерн",
    },
    {
      title: "Классика",
      text: "Фасады с выразительной фактурой, тёплая палитра и привычная домашняя атмосфера.",
      image: "work_4495",
      alt: "Классическая кухня",
    },
  ],
  process: [
    ["Оставляете заявку", "В MAX-боте кратко рассказываете о будущей кухне и добавляете фото помещения."],
    ["Разбираем задачу", "Я смотрю планировку, пожелания, технику и заранее отмечаю важные нюансы."],
    ["Встречаемся на замере", "Уточняем размеры, розетки, воду, газ и все привязки на месте."],
    ["Согласовываем проект", "Подбираем материалы, наполнение и финальную конфигурацию кухни."],
    ["Изготавливаем кухню", "Собираем изделие в цехе под согласованный проект."],
    ["Доставляем и монтируем", "Привозим, устанавливаем и сдаём готовую кухню на объекте."],
  ],
  faq: [
    ["Можно ли заказать кухню по фотографии?", "Фото поможет обсудить идею и планировку. Точные размеры и технические нюансы уточняем на замере."],
    ["Что делает MAX-бот?", "Бот помогает собрать пожелания и фото помещения в одну заявку, чтобы к разговору с Артёмом уже было понятно направление проекта."],
    ["Можно ли посмотреть материалы до заказа?", "Да. На встрече и при согласовании проекта выбираем фасады, столешницу, фурнитуру и оттенки под вашу задачу."],
    ["Делаете ли доставку и монтаж?", "Да. Изготавливаем, доставляем и устанавливаем кухню на объекте."],
  ],
};

const icon = {
  max: `<img class="max-logo-icon" src="${asset("media/brand/max_icon.png")}" alt="" aria-hidden="true" decoding="async">`,
  arrow: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h12.2m-4.7-5 5 5-5 5"/></svg>',
  chevronLeft: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 6-6 6 6 6"/></svg>',
  chevronRight: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>',
  chevronDown: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
  menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>',
};

function kitchenImage(id, variant = "card") {
  return {
    webp: `media/kitchens_real/${id}_${variant}.webp`,
    jpg: `media/kitchens_real/${id}_${variant}.jpg`,
  };
}

function picture({ webp, jpg, alt, className = "", loading = "eager" }) {
  return `<picture class="${className}"><source srcset="${asset(webp)}" type="image/webp"><img src="${asset(jpg)}" alt="${alt}" loading="${loading}" decoding="async"></picture>`;
}

function cta(label, source, variant = "primary") {
  return `<button class="button button-${variant} pseudo-cta" type="button" aria-disabled="true" data-cta="${source}">${icon.max}<span>${label}</span>${icon.arrow}</button>`;
}

function nav() {
  return [
    ["#works", "Работы"],
    ["#about", "Обо мне"],
    ["#generator", "MAX-бот"],
    ["#styles", "Варианты"],
    ["#process", "Как работаем"],
    ["#contacts", "Контакты"],
  ].map(([href, label]) => `<a href="${href}">${label}</a>`).join("");
}

function renderHeader() {
  return `<header class="site-header" data-header>
    <a class="brand" href="#top" aria-label="${site.brand.name}">${picture({ ...site.brand.logo, className: "brand-logo", loading: "eager" })}</a>
    <nav class="desktop-nav" aria-label="Основная навигация">${nav()}</nav>
    <button class="header-cta pseudo-cta" type="button" aria-disabled="true" data-cta="website_main">${icon.max}<span>Перейти в MAX</span></button>
    <button class="menu-button" type="button" aria-label="Открыть меню" data-menu-toggle>${icon.menu}</button>
    <div class="mobile-panel" data-mobile-panel>
      <button class="menu-close" type="button" aria-label="Закрыть меню" data-menu-close>${icon.close}</button>
      <nav aria-label="Мобильная навигация">${nav()}</nav>
      ${cta("Перейти в MAX", "website_main")}
    </div>
  </header>`;
}

function renderHero() {
  return `<section class="hero section" id="top">
    <div class="hero-copy">
      <p class="eyebrow">Мебельный салон «Интерьер»</p>
      <h1>${site.hero.title}</h1>
      <p class="lead">${site.hero.text}</p>
      <div class="hero-actions">
        <div class="hero-primary-action">${cta("Подобрать кухню в MAX", "website_main")}<small>Подбор идеи и заявка в одном диалоге</small></div>
        <a class="button button-ghost" href="#works"><span>Посмотреть работы</span>${icon.arrow}</a>
      </div>
    </div>
    <div class="hero-media">${picture({ ...site.hero.image, className: "hero-picture", loading: "eager" })}</div>
  </section>`;
}

function renderAdvantages() {
  return `<section class="section advantages" aria-label="Преимущества">
    ${site.advantages.map(([value, text]) => `<div><strong>${value}</strong><span>${text}</span></div>`).join("")}
  </section>`;
}

function renderGalleryCards(items, mode = "") {
  return items.map((item) => {
    const image = kitchenImage(item.image, "card");
    const full = kitchenImage(item.image, "fullscreen");
    return `<article class="work-item ${mode}" data-lightbox="${asset(full.jpg)}" data-title="${item.title}">
      <button class="work-image" type="button" aria-label="Открыть фото: ${item.title}">
        ${picture({ ...image, alt: item.alt, className: "work-picture" })}
        <span class="work-caption"><em>${item.type}</em><strong>${item.title}</strong></span>
      </button>
    </article>`;
  }).join("");
}

function renderGallery() {
  const featured = site.gallery.slice(0, 6);
  const more = site.gallery.slice(6);
  return `<section class="section works" id="works">
    <div class="section-heading"><div><p class="eyebrow">Портфолио</p><h2>Наши работы</h2></div><p>Кухни, которые уже собраны и установлены в Людинове и ближайших районах.</p></div>
    <div class="works-showcase"><div class="carousel-toolbar" aria-label="Листать работы"><button class="carousel-button" type="button" aria-label="Предыдущая кухня" data-carousel-prev>${icon.chevronLeft}</button><button class="carousel-button" type="button" aria-label="Следующая кухня" data-carousel-next>${icon.chevronRight}</button></div><div class="works-carousel" data-work-carousel>${renderGalleryCards(featured, "carousel-card")}</div></div>
    <button class="more-works" type="button" aria-expanded="false" data-more-works><span>Все работы</span>${icon.chevronDown}</button>
    <div class="works-extra" data-works-extra hidden>${renderGalleryCards(more, "extra-card")}</div>
    <div class="inline-cta">${cta("Подобрать свою кухню в MAX", "website_works", "secondary")}</div>
  </section>`;
}

function renderAbout() {
  const photo = { webp: "media/kitchens_real/owner_in_showroom_card.webp", jpg: "media/kitchens_real/owner_in_showroom_card.jpg", alt: "Артём Ермаков в салоне кухни" };
  return `<section class="section about" id="about">
    <div class="about-image">${picture({ ...photo, className: "about-picture" })}</div>
    <div><p class="eyebrow">${site.owner.role}</p><h2>Меня зовут Артём Ермаков</h2>
      <p>Мы занимаемся изготовлением кухонь и мебели на заказ уже больше 10 лет. За это время реализовали сотни проектов для Людинова и ближайших районов области.</p>
      <p>Я лично участвую во всех этапах каждого заказа: от замера до установки. Если нужен надёжный партнёр, который отвечает за сроки и качество, будем рады обсудить ваш проект без лишней суеты.</p>
      <blockquote>«Я ручаюсь за качество каждого изделия, которое выходит из нашего цеха. Если вам что-то не понравится, я решу вопрос лично».</blockquote>
      <div class="inline-cta">${cta("Обсудить кухню в MAX", "website_about", "secondary")}</div>
    </div>
  </section>`;
}

function renderGenerator() {
  return `<section class="section generator" id="generator">
    <div class="section-heading"><div><p class="eyebrow">MAX-бот</p><h2>Соберите идею кухни в MAX</h2></div><p>Коротко расскажите о задаче, добавьте фото помещения и отправьте заявку Артёму.</p></div>
    <ol class="generator-steps">${site.generatorSteps.map(([number, title, text]) => `<li><span>${number}</span><strong>${title}</strong><p>${text}</p></li>`).join("")}</ol>
    <div class="section-cta slim generator-cta">${cta("Перейти в MAX", "website_generator")}</div>
  </section>`;
}

function renderStyles() {
  return `<section class="section styles" id="styles"><div class="section-heading compact"><div><p class="eyebrow">Направления</p><h2>Какой стиль вам ближе</h2></div></div><div class="style-grid">${site.styles.map((style) => {
    const image = kitchenImage(style.image, "card");
    return `<article class="style-card">${picture({ ...image, alt: style.alt, className: "style-picture" })}<div><h3>${style.title}</h3><p>${style.text}</p></div></article>`;
  }).join("")}</div><div class="inline-cta">${cta("Подобрать стиль в MAX", "website_styles", "secondary")}</div></section>`;
}

function renderProcess() {
  return `<section class="section process" id="process"><div class="section-heading compact"><div><p class="eyebrow">По делу</p><h2>Как я работаю</h2></div></div><ol class="process-list">${site.process.map(([title, text], index) => `<li><span>${String(index + 1).padStart(2, "0")}</span><div><h3>${title}</h3><p>${text}</p></div></li>`).join("")}</ol><div class="inline-cta">${cta("Начать подбор в MAX", "website_process", "secondary")}</div></section>`;
}

function renderFaq() {
  return `<section class="section faq" id="faq"><div class="section-heading compact"><div><p class="eyebrow">Важно знать</p><h2>Ответы на вопросы</h2></div></div><div class="faq-list">${site.faq.map(([question, answer]) => `<details><summary>${question}</summary><p>${answer}</p></details>`).join("")}</div></section>`;
}

function renderContacts() {
  return `<section class="section contacts" id="contacts"><div><p class="eyebrow">Связь</p><h2>Обсудим вашу кухню</h2><p>Опишите задачу в MAX-боте, а Артём посмотрит заявку и поможет определить следующий шаг.</p>${cta("Перейти в MAX", "website_contacts")}</div><dl class="contact-list"><div><dt>Телефон</dt><dd>${site.contacts.phone}</dd></div><div><dt>Адрес</dt><dd>${site.contacts.address}</dd></div><div><dt>Регион работы</dt><dd>${site.contacts.region}</dd></div><div><dt>Часы связи</dt><dd>${site.contacts.hours}</dd></div></dl></section>`;
}

function renderFooter() {
  return `<footer class="footer"><p>${site.brand.name}</p><p>Кухни и мебель на заказ в Людинове и ближайших районах.</p></footer>`;
}

function renderApp() {
  document.querySelector("#app").innerHTML = `${renderHeader()}<main>${renderHero()}${renderAdvantages()}${renderGallery()}${renderAbout()}${renderGenerator()}${renderStyles()}${renderProcess()}${renderFaq()}${renderContacts()}</main>${renderFooter()}<div class="lightbox" data-lightbox-modal hidden><button type="button" aria-label="Закрыть фото" data-lightbox-close>${icon.close}</button><img src="" alt=""><div><strong data-lightbox-title></strong></div></div>`;
}

function bindMenu() {
  const panel = document.querySelector("[data-mobile-panel]");
  const open = document.querySelector("[data-menu-toggle]");
  const close = document.querySelector("[data-menu-close]");
  const setOpen = (value) => { panel.classList.toggle("is-open", value); document.body.classList.toggle("has-menu", value); };
  open.addEventListener("click", () => setOpen(true));
  close.addEventListener("click", () => setOpen(false));
  panel.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setOpen(false)));
}

function bindWorkShowcase() {
  const rail = document.querySelector("[data-work-carousel]");
  const prev = document.querySelector("[data-carousel-prev]");
  const next = document.querySelector("[data-carousel-next]");
  const moreButton = document.querySelector("[data-more-works]");
  const moreGrid = document.querySelector("[data-works-extra]");
  if (!rail) return;
  const cardStep = () => (rail.querySelector(".work-item")?.getBoundingClientRect().width || 360) + 16;
  const scrollCarousel = (direction = 1) => {
    const atEnd = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 24;
    if (direction > 0 && atEnd) rail.scrollTo({ left: 0, behavior: "smooth" });
    else rail.scrollBy({ left: cardStep() * direction, behavior: "smooth" });
  };
  prev?.addEventListener("click", () => scrollCarousel(-1));
  next?.addEventListener("click", () => scrollCarousel(1));
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    let autoplay = window.setInterval(() => scrollCarousel(1), 4800);
    const stop = () => { if (autoplay) { window.clearInterval(autoplay); autoplay = null; } };
    const start = () => { if (!autoplay) autoplay = window.setInterval(() => scrollCarousel(1), 4800); };
    rail.addEventListener("pointerenter", stop); rail.addEventListener("pointerleave", start); rail.addEventListener("focusin", stop); rail.addEventListener("focusout", start);
  }
  moreButton?.addEventListener("click", () => {
    const isOpen = moreButton.getAttribute("aria-expanded") === "true";
    moreButton.setAttribute("aria-expanded", String(!isOpen));
    moreButton.querySelector("span").textContent = isOpen ? "Все работы" : "Скрыть работы";
    moreGrid.hidden = isOpen;
  });
}

function bindGallery() {
  const modal = document.querySelector("[data-lightbox-modal]");
  const image = modal.querySelector("img");
  const title = modal.querySelector("[data-lightbox-title]");
  document.addEventListener("click", (event) => {
    const item = event.target.closest("[data-lightbox]");
    if (!item) return;
    image.src = item.dataset.lightbox; image.alt = item.dataset.title; title.textContent = item.dataset.title;
    modal.hidden = false; document.body.classList.add("has-lightbox");
  });
  const close = () => { modal.hidden = true; image.removeAttribute("src"); document.body.classList.remove("has-lightbox"); };
  modal.querySelector("[data-lightbox-close]").addEventListener("click", close);
  modal.addEventListener("click", (event) => { if (event.target === modal) close(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !modal.hidden) close(); });
}

function bindHeader() {
  const header = document.querySelector("[data-header]");
  const update = () => header.classList.toggle("is-scrolled", window.scrollY > 12);
  update(); window.addEventListener("scroll", update, { passive: true });
}

renderApp();
bindHeader();
bindMenu();
bindWorkShowcase();
bindGallery();
