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
    role: "лично веду проекты кухонь",
  },
  contacts: {
    maxBotUrl: "",
    phone: "+7 (XXX) XXX-XX-XX",
    address: "—",
    region: "—",
    hours: "Пн-Пт: 9:00-18:00",
  },
  hero: {
    title: "Я Артём. Соберу кухню под ваш дом.",
    text:
      "Лично разбираю планировку, материалы и бюджет, а команда изготавливает и монтирует кухню под размеры вашего помещения.",
    note: "Начните с фото помещения - бот соберёт пожелания и передаст заявку администратору без длинной переписки.",
    image: {
      webp: "media/kitchens_real/owner_at_kitchen_hero.webp",
      jpg: "media/kitchens_real/owner_at_kitchen_hero.jpg",
      alt: "Артём Ермаков на фоне серой кухни на заказ",
    },
  },
  advantages: [
    "Я лично веду проект",
    "Реальные работы на фото",
    "Подбор под бюджет",
    "Изготовление и монтаж",
  ],
  generatorSteps: [
    ["1", "Выбираете форму", "Прямая, угловая, П-образная или островная."],
    ["2", "Загружаете фото", "Показываете помещение, где будет стоять кухня."],
    ["3", "Получаете визуальный вариант", "Видите направление по цвету, фасадам и рабочим зонам."],
    ["4", "Заявка уходит Артёму", "Я смотрю подбор и возвращаюсь со следующим шагом."],
  ],
  gallery: [
    {
      id: "work_4486",
      title: "Угловая кухня с зелёным акцентом",
      type: "Угловая",
      image: "work_4486",
      alt: "Угловая кухня с зелёными нижними фасадами",
      ratio: "wide",
    },
    {
      id: "work_4493",
      title: "Серо-белая угловая кухня",
      type: "Угловая",
      image: "work_4493",
      alt: "Серо-белая угловая кухня",
      ratio: "wide",
    },
    {
      id: "work_4481",
      title: "Светлая кухня с пеналами",
      type: "Светлая",
      image: "work_4481",
      alt: "Светлая кухня с пеналами и встроенной техникой",
      ratio: "tall",
    },
    {
      id: "work_4491",
      title: "Угловая кухня с древесной столешницей",
      type: "Угловая",
      image: "work_4491",
      alt: "Кухня в графитовых и древесных оттенках",
      ratio: "wide",
    },
    {
      id: "work_4488",
      title: "Зелёно-белая кухня с длинной рабочей зоной",
      type: "Рабочая зона",
      image: "work_4488",
      alt: "Кухня с зелёными фасадами и светлой столешницей",
      ratio: "wide",
    },
    {
      id: "work_4495",
      title: "Классическая угловая кухня",
      type: "Угловая",
      image: "work_4495",
      alt: "Классическая белая кухня",
      ratio: "wide",
    },
    {
      id: "work_4482",
      title: "Угловая кухня с тёплой подсветкой",
      type: "Угловая",
      image: "work_4482",
      alt: "Серая кухня с тёплой подсветкой",
    },
    {
      id: "work_4489",
      title: "Угловая кухня с встроенной техникой",
      type: "Угловая",
      image: "work_4489",
      alt: "Серая кухня с встроенной техникой",
    },
    {
      id: "work_4492",
      title: "Компактная линейная кухня",
      type: "Линейная",
      image: "work_4492",
      alt: "Компактная кухня в серых оттенках",
    },
    {
      id: "work_4485",
      title: "Светлая рабочая зона без ручек",
      type: "Рабочая зона",
      image: "work_4485",
      alt: "Светлая рабочая линия кухни",
    },
    {
      id: "work_4487",
      title: "Фрагмент серой кухни",
      type: "Рабочая зона",
      image: "work_4487",
      alt: "Рабочая зона кухни с серыми фасадами",
    },
    {
      id: "work_4490",
      title: "Рабочая линия кухни",
      type: "Деталь",
      image: "work_4490",
      alt: "Столешница и варочная зона кухни",
    },
    {
      id: "work_4494",
      title: "П-образная кухня в зелёном цвете",
      type: "П-образная",
      image: "work_4494",
      alt: "П-образная зелёная кухня в компактном помещении",
      ratio: "tall",
    },
    {
      id: "work_4496",
      title: "Небольшая угловая кухня",
      type: "Угловая",
      image: "work_4496",
      alt: "Небольшая кухня в светло-серых оттенках",
      ratio: "tall",
    },
  ],
  options: {
    layouts: ["Прямая", "Угловая", "П-образная", "С островом"],
    styles: ["Современный", "Неоклассика", "Классика"],
    colors: ["Серый", "Бежевый", "Зелёный", "Белый"],
    handles: ["Ручка-скоба", "Чёрная квадратная ручка", "Ручка-кнопка", "Профиль Gola"],
    facades: ["Interno", "AGT", "Другие варианты"],
    hardware: ["Tandembox", "Направляющие скрытого монтажа", "Blum", "Hettich", "Boyard"],
  },
  materials: [
    {
      title: "Гладкие фасады",
      text: "Матовые и глянцевые решения под современную кухню без визуального шума.",
      image: "media/kitchens_real/work_4493_card.webp",
      fallback: "media/kitchens_real/work_4493_card.jpg",
      alt: "Гладкие фасады на серо-белой угловой кухне",
    },
    {
      title: "Столешницы и панели",
      text: "Подбираем каменные, светлые и древесные фактуры под нагрузку и стиль.",
      image: "media/kitchens_real/work_4491_card.webp",
      fallback: "media/kitchens_real/work_4491_card.jpg",
      alt: "Кухня с древесной столешницей и графитовыми фасадами",
    },
    {
      title: "Ручки и открывание",
      text: "Профиль Gola, интегрированные решения или ручки, которые удобно держать каждый день.",
      image: "media/kitchens_real/work_4490_card.webp",
      fallback: "media/kitchens_real/work_4490_card.jpg",
      alt: "Деталь кухни с ручками и рабочей поверхностью",
    },
    {
      title: "Техника и хранение",
      text: "Сразу учитываем духовой шкаф, мойку, вытяжку, пеналы и удобные зоны хранения.",
      image: "media/kitchens_real/work_4489_card.webp",
      fallback: "media/kitchens_real/work_4489_card.jpg",
      alt: "Компактная кухня со встроенной техникой",
    },
  ],
  process: [
    ["Подбор", "Вы отвечаете на короткие вопросы в MAX-боте."],
    ["Визуализация", "Бот собирает вводные и готовит изображение будущей кухни по фото помещения."],
    ["Разбор заявки", "Я смотрю планировку, материалы, технику и нюансы помещения."],
    ["Замер", "Уточняем размеры, выводы, розетки, газ, воду и технику."],
    ["Изготовление", "Изготавливаем кухню под согласованный проект."],
    ["Монтаж", "Привозим, собираем и сдаём готовую кухню."],
  ],
  reviews: [],
  faq: [
    [
      "Можно ли изготовить кухню по фотографии?",
      "Да. Фото помещения помогает понять планировку, привязки, свет и общий стиль. Точный проект всё равно уточняется после замера.",
    ],
    [
      "Что делает бот MAX?",
      "Бот собирает форму кухни, стиль, цвет, материалы и фото помещения, чтобы Артём сразу видел цельную заявку.",
    ],
    [
      "Будет ли визуализация по моему фото?",
      "Да, сценарий рассчитан на визуализацию идеи кухни в вашем помещении. Это предварительный образ для подбора, не рабочий чертёж.",
    ],
    [
      "Какие материалы используются?",
      "В подборе доступны основные варианты фасадов, цветов, ручек, столешниц и фурнитуры. Конкретные позиции уточняются после просмотра заявки и замера.",
    ],
    [
      "Делаете ли доставку и монтаж?",
      "Да, этот этап предусмотрен в процессе работы. Детали зависят от адреса и состава проекта.",
    ],
    [
      "Можно ли встроить технику?",
      "Да, при проектировании учитываются встроенная техника, розетки, вытяжка, мойка и рабочие зоны.",
    ],
  ],
};

const icon = {
  max:
    `<img class="max-logo-icon" src="${asset("media/brand/max_icon.png")}" alt="" aria-hidden="true" decoding="async">`,
  arrow:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h12.2m-4.7-5 5 5-5 5"/></svg>',
  chevronLeft:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 6-6 6 6 6"/></svg>',
  chevronRight:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>',
  chevronDown:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
  menu:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  close:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>',
};

function kitchenImage(id, variant = "card") {
  return {
    webp: `media/kitchens_real/${id}_${variant}.webp`,
    jpg: `media/kitchens_real/${id}_${variant}.jpg`,
  };
}

function picture({ webp, jpg, alt, className = "", loading = "lazy" }) {
  return `
    <picture class="${className}">
      <source srcset="${asset(webp)}" type="image/webp">
      <img src="${asset(jpg)}" alt="${alt}" loading="${loading}" decoding="async">
    </picture>
  `;
}

function cta(label, source, variant = "primary") {
  return `
    <button class="button button-${variant} pseudo-cta" type="button" aria-disabled="true" data-cta="${source}">
      ${icon.max}
      <span>${label}</span>
      ${icon.arrow}
    </button>
  `;
}

function nav() {
  const items = [
    ["#works", "Работы"],
    ["#about", "Обо мне"],
    ["#generator", "MAX-бот"],
    ["#options", "Материалы"],
    ["#process", "Как работаем"],
    ["#contacts", "Контакты"],
  ];
  return items.map(([href, label]) => `<a href="${href}">${label}</a>`).join("");
}

function renderHeader() {
  return `
    <header class="site-header" data-header>
      <a class="brand" href="#top" aria-label="${site.brand.name}">
        ${picture({ ...site.brand.logo, className: "brand-logo", loading: "eager" })}
      </a>
      <nav class="desktop-nav" aria-label="Основная навигация">${nav()}</nav>
      <button class="header-cta pseudo-cta" type="button" aria-disabled="true" data-cta="website_main">${icon.max}<span>Перейти в MAX</span></button>
      <button class="menu-button" type="button" aria-label="Открыть меню" data-menu-toggle>${icon.menu}</button>
      <div class="mobile-panel" data-mobile-panel>
        <button class="menu-close" type="button" aria-label="Закрыть меню" data-menu-close>${icon.close}</button>
        <nav aria-label="Мобильная навигация">${nav()}</nav>
        ${cta("Перейти в MAX", "website_main")}
      </div>
    </header>
  `;
}

function renderHero() {
  const [firstSentence, ...rest] = site.hero.title.split(". ");
  const titleTail = rest.join(". ");
  return `
    <section class="hero section" id="top">
      <div class="hero-copy">
        <h1><span>${firstSentence}.</span> ${titleTail}</h1>
        <p class="lead">${site.hero.text}</p>
        <div class="hero-actions">
          <div class="hero-primary-action">
            ${cta("Перейти в MAX", "website_main")}
            <small>Быстрый подбор и визуализация по фото</small>
          </div>
          <a class="button button-ghost" href="#works"><span>Смотреть кухни</span>${icon.arrow}</a>
        </div>
        <p class="hero-note">${site.hero.note}</p>
        <ul class="advantage-strip">
          ${site.advantages.map((item) => `<li>${item}</li>`).join("")}
        </ul>
      </div>
      <div class="hero-media">
        ${picture({ ...site.hero.image, className: "hero-picture", loading: "eager" })}
      </div>
    </section>
  `;
}

function renderGenerator() {
  return `
    <section class="section generator" id="generator">
      <div class="section-heading compact">
        <h2>Соберите кухню мечты в MAX-боте</h2>
      </div>
      <div class="generator-layout">
        <ol class="generator-steps">
          ${site.generatorSteps
            .map(
              ([number, title, text]) => `
                <li>
                  <span>${number}</span>
                  <strong>${title}</strong>
                  <p>${text}</p>
                </li>
              `,
            )
            .join("")}
        </ol>
      </div>
      <div class="section-cta slim generator-cta">
        ${cta("Перейти в MAX", "website_generator")}
      </div>
    </section>
  `;
}

function renderGalleryCards(items, mode = "") {
  return items
    .map((item) => {
      const image = kitchenImage(item.image, "card");
      const full = kitchenImage(item.image, "fullscreen");
      return `
        <article class="work-item ${mode} ${item.ratio || ""}" data-lightbox="${asset(full.jpg)}" data-title="${item.title}">
          <button class="work-image" type="button" aria-label="Открыть фото: ${item.title}">
            ${picture({ ...image, alt: item.alt, className: "work-picture" })}
            <span class="work-caption"><em>${item.type}</em><strong>${item.title}</strong></span>
          </button>
        </article>
      `;
    })
    .join("");
}

function renderGallery() {
  const featured = site.gallery.slice(0, 6);
  const more = site.gallery.slice(6);
  return `
    <section class="section works" id="works">
      <div class="section-heading compact">
        <h2>Реальные кухни</h2>
      </div>
      <div class="works-showcase">
        <div class="carousel-toolbar" aria-label="Листать реальные кухни">
          <button class="carousel-button" type="button" aria-label="Предыдущая кухня" data-carousel-prev>${icon.chevronLeft}</button>
          <button class="carousel-button" type="button" aria-label="Следующая кухня" data-carousel-next>${icon.chevronRight}</button>
        </div>
        <div class="works-carousel" data-work-carousel>${renderGalleryCards(featured, "carousel-card")}</div>
      </div>
      <button class="more-works" type="button" aria-expanded="false" data-more-works>
        <span>Показать ещё кухни</span>
        ${icon.chevronDown}
      </button>
      <div class="works-extra" data-works-extra hidden>${renderGalleryCards(more, "extra-card")}</div>
    </section>
  `;
}

function renderOptions() {
  const groups = [
    ["01", "Планировка", "От формы зависит удобство маршрута: мойка, плита, хранение.", site.options.layouts],
    ["02", "Стиль", "Подбираем направление, которое нормально живёт в вашем интерьере.", site.options.styles],
    ["03", "Цвет", "Смотрим не только красивый образец, но и свет в помещении.", site.options.colors],
    ["04", "Открывание", "Ручки, профиль или скрытые решения под ежедневное использование.", site.options.handles],
    ["05", "Фасады", "От спокойной базы до выразительных фактур под бюджет проекта.", site.options.facades],
    ["06", "Фурнитура", "Направляющие и механизмы под нагрузку, размер и сценарий хранения.", site.options.hardware],
  ];
  return `
    <section class="section options" id="options">
      <div class="section-heading compact">
        <h2>Что подберём</h2>
      </div>
      <div class="option-groups">
        ${groups
          .map(
            ([number, title, text, items]) => `
              <div class="option-group">
                <span>${number}</span>
                <h3>${title}</h3>
                <p>${text}</p>
                <div>${items.map((item) => `<span>${item}</span>`).join("")}</div>
              </div>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderMaterials() {
  return `
    <section class="section materials" id="materials">
      <div class="section-heading compact">
        <h2>Материалы на реальных кухнях</h2>
      </div>
      <div class="material-rail">
        ${site.materials
          .map(
            (item) => `
              <figure class="material-item">
                ${picture({ webp: item.image, jpg: item.fallback, alt: item.alt || item.title, className: "material-picture" })}
                <figcaption>${item.title}</figcaption>
                <p>${item.text}</p>
              </figure>
            `,
          )
          .join("")}
      </div>
      <div class="section-cta slim">
        ${cta("Подобрать материалы в MAX", "website_generator", "secondary")}
      </div>
    </section>
  `;
}

function renderAbout() {
  return `
    <section class="section about" id="about">
      <div>
        <h2>Обо мне</h2>
        <p>Я Артём. Мне важно, чтобы кухня была не “как в салоне сказали”, а как удобно именно вам: где будет мойка, как встанет техника, сколько останется рабочей поверхности и где можно не переплачивать.</p>
        <p>Я лично смотрю заявку и веду проект до понятного следующего шага. Производство и монтаж не исчезают где-то “у подрядчиков”: я остаюсь в связке с задачей.</p>
        <ul class="about-facts">
          <li><strong>15+ лет</strong><span>опыта в кухнях и мебели</span></li>
          <li><strong>Лично</strong><span>смотрю планировку и материалы</span></li>
          <li><strong>Под ключ</strong><span>от идеи до монтажа</span></li>
        </ul>
      </div>
      <div class="about-image">
        ${picture({ ...site.hero.image, className: "about-picture" })}
      </div>
    </section>
  `;
}

function renderProcess() {
  return `
    <section class="section process" id="process">
      <div class="section-heading compact">
        <h2>Как я работаю</h2>
      </div>
      <ol class="process-list">
        ${site.process
          .map(
            ([title, text], index) => `
              <li>
                <span>${index + 1}</span>
                <div>
                  <h3>${title}</h3>
                  <p>${text}</p>
                </div>
              </li>
            `,
          )
          .join("")}
      </ol>
    </section>
  `;
}

function renderReviews() {
  if (!site.reviews.length) return "";
  return `
    <section class="section reviews" id="reviews">
      <div class="section-heading">
        <h2>Отзывы</h2>
      </div>
    </section>
  `;
}

function renderFaq() {
  return `
    <section class="section faq" id="faq">
      <div class="section-heading compact">
        <h2>Ответы на вопросы</h2>
      </div>
      <div class="faq-list">
        ${site.faq
          .map(
            ([question, answer]) => `
              <details>
                <summary>${question}</summary>
                <p>${answer}</p>
              </details>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderContacts() {
  return `
    <section class="section contacts" id="contacts">
      <div>
        <h2>Контакты</h2>
        <p>Перейдите в бот, отправьте фото помещения и пожелания. Артём увидит подбор и вернётся с понятным следующим шагом.</p>
        ${cta("Перейти в MAX", "website_main")}
      </div>
      <dl class="contact-list">
        <div><dt>Телефон</dt><dd>${site.contacts.phone}</dd></div>
        <div><dt>Бот</dt><dd>${site.contacts.maxBotUrl ? site.contacts.maxBotUrl : "MAX-бот для подбора кухни"}</dd></div>
        <div><dt>Адрес</dt><dd>${site.contacts.address}</dd></div>
        <div><dt>Регион работы</dt><dd>${site.contacts.region}</dd></div>
        <div><dt>Часы связи</dt><dd>${site.contacts.hours}</dd></div>
      </dl>
    </section>
  `;
}

function renderFooter() {
  return `
    <footer class="footer">
      <p>${site.brand.name}</p>
      <p>Кухни на заказ, личный подбор Артёма, изготовление и монтаж.</p>
    </footer>
  `;
}

function renderApp() {
  document.querySelector("#app").innerHTML = `
    ${renderHeader()}
    <main>
      ${renderHero()}
      ${renderGallery()}
      ${renderAbout()}
      ${renderGenerator()}
      ${renderOptions()}
      ${renderMaterials()}
      ${renderProcess()}
      ${renderReviews()}
      ${renderFaq()}
      ${renderContacts()}
    </main>
    ${renderFooter()}
    <div class="lightbox" data-lightbox-modal hidden>
      <button type="button" aria-label="Закрыть фото" data-lightbox-close>${icon.close}</button>
      <img src="" alt="">
      <div>
        <strong data-lightbox-title></strong>
      </div>
    </div>
  `;
}

async function hydrateRemoteContent() {
  const apiBase = import.meta.env.VITE_API_BASE_URL;
  if (!apiBase) return;
  try {
    const response = await fetch(`${apiBase.replace(/\/$/, "")}/api/site-content`, {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) return;
    const remote = await response.json();
    if (remote.contacts) {
      site.contacts = {
        ...site.contacts,
        phone: remote.contacts.phone || site.contacts.phone,
        address: remote.contacts.address || site.contacts.address,
        region: remote.contacts.region || site.contacts.region,
        hours: remote.contacts.hours || site.contacts.hours,
      };
    }
    if (remote.blocks?.hero_title?.content) {
      site.hero.title = remote.blocks.hero_title.content;
    }
    if (remote.blocks?.hero_subtitle?.content) {
      site.hero.text = remote.blocks.hero_subtitle.content;
    }
  } catch (error) {
    console.info("API content is unavailable, using static fallback.", error);
  }
}

function bindMenu() {
  const panel = document.querySelector("[data-mobile-panel]");
  const open = document.querySelector("[data-menu-toggle]");
  const close = document.querySelector("[data-menu-close]");
  const setOpen = (value) => {
    panel.classList.toggle("is-open", value);
    document.body.classList.toggle("has-menu", value);
  };
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

  const cardStep = () => {
    const card = rail.querySelector(".work-item");
    return card ? card.getBoundingClientRect().width + 16 : 360;
  };

  const scrollCarousel = (direction = 1) => {
    const atEnd = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 24;
    if (direction > 0 && atEnd) {
      rail.scrollTo({ left: 0, behavior: "smooth" });
      return;
    }
    rail.scrollBy({ left: cardStep() * direction, behavior: "smooth" });
  };

  prev?.addEventListener("click", () => scrollCarousel(-1));
  next?.addEventListener("click", () => scrollCarousel(1));

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let autoplay = null;
  const startAutoplay = () => {
    if (reducedMotion || autoplay) return;
    autoplay = window.setInterval(() => scrollCarousel(1), 4200);
  };
  const stopAutoplay = () => {
    if (!autoplay) return;
    window.clearInterval(autoplay);
    autoplay = null;
  };

  rail.addEventListener("pointerenter", stopAutoplay);
  rail.addEventListener("pointerleave", startAutoplay);
  rail.addEventListener("focusin", stopAutoplay);
  rail.addEventListener("focusout", startAutoplay);
  startAutoplay();

  moreButton?.addEventListener("click", () => {
    const isOpen = moreButton.getAttribute("aria-expanded") === "true";
    moreButton.setAttribute("aria-expanded", String(!isOpen));
    moreButton.querySelector("span").textContent = isOpen ? "Показать ещё кухни" : "Скрыть дополнительные кухни";
    moreGrid.hidden = isOpen;
    if (!isOpen) {
      moreGrid.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}

function bindGallery() {
  const modal = document.querySelector("[data-lightbox-modal]");
  const image = modal.querySelector("img");
  const title = modal.querySelector("[data-lightbox-title]");

  document.addEventListener("click", (event) => {
    const item = event.target.closest("[data-lightbox]");
    if (!item) return;
    image.src = item.dataset.lightbox;
    image.alt = item.dataset.title;
    title.textContent = item.dataset.title;
    modal.hidden = false;
    document.body.classList.add("has-lightbox");
  });

  const closeModal = () => {
    modal.hidden = true;
    image.removeAttribute("src");
    document.body.classList.remove("has-lightbox");
  };
  modal.querySelector("[data-lightbox-close]").addEventListener("click", closeModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) closeModal();
  });
}

function bindHeader() {
  const header = document.querySelector("[data-header]");
  const update = () => header.classList.toggle("is-scrolled", window.scrollY > 12);
  update();
  window.addEventListener("scroll", update, { passive: true });
}

await hydrateRemoteContent();
renderApp();
bindHeader();
bindMenu();
bindWorkShowcase();
bindGallery();
