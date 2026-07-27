# Design

## Source of truth
- Status: Active
- Last refreshed: 2026-07-27
- Primary product surfaces: публичный сайт мебельного салона, переход в MAX-бот, админка контента.
- Evidence reviewed: клиентский промпт от 2026-07-27, `frontend/src/main.js`, `frontend/src/styles.css`, логотип в `assets/raw/brand/logo_interier_header.svg`, реальные фотографии Артёма и готовых кухонь в `assets/raw/kitchens_real/`.

## Brand
- Personality: уверенный, личный, современный мебельный бизнес без показной роскоши.
- Trust signals: Артём как основатель, реальные работы, цена от 150 000 ₽, собственное производство, отзывы Яндекс Карт.
- Avoid: шаблонный каталог стилей, неподтверждённые сроки, стоковые/сгенерированные портреты, визуальная перегруженность.

## Product goals
- Goals: показать конкретную выгоду, вызвать доверие к Артёму, привести в MAX-бот на подбор проекта.
- Non-goals: заменять точный расчёт ботом; перегружать пользователя десятками карточек и объяснений.
- Success signals: переход в MAX, звонок, просмотр реальных работ и отзывов.

## Personas and jobs
- Primary personas: жители Людинова и ближайших районов, планирующие кухню или мебель на заказ.
- User jobs: быстро понять цену и исполнителя, увидеть реальные работы, начать подбор без звонка.
- Key contexts of use: мобильный телефон после рекламы; десктоп при сравнении исполнителей.

## Information architecture
- Primary navigation: Работы, Как заказать, Обо мне, Отзывы, Контакты.
- Core routes/screens: одностраничный сайт, MAX-бот, админка.
- Content hierarchy: ценность и Артём -> преимущества -> работы -> MAX -> производство/личная ответственность -> отзывы -> контакт.

## Design principles
- Сначала конкретика: цена, личная ответственность и реальные фотографии прежде декоративных элементов.
- Тёмная сцена подчёркивает качество, красный используется только для действия и важных меток.
- Изображение Артёма и текст не пересекаются на любом экране.
- Tradeoffs: фон кухни не дорисовывается AI, чтобы не менять внешность и не выдавать вымысел за реальность.

## Visual language
- Color: `#111315` graphite, `#FFFFFF` typography, `#E53935` action accent, тёплые световые наложения только вокруг изображений кухни.
- Typography: нейтральный системный grotesk, крупный плотный заголовок, удобный межстрочный интервал в текстах.
- Spacing/layout rhythm: 8px base, широкая 12-колоночная сетка на desktop, одна колонка на mobile.
- Shape/radius/elevation: радиус 6px, тонкие границы, без декоративных плавающих карточек.
- Motion: короткий hover для CTA и фото, уважение `prefers-reduced-motion`.
- Imagery/iconography: только предоставленные фото и line-иконки в красном цвете.

## Components
- Existing components to reuse: `maxCta`, карточки работ, карусель отзывов, лайтбокс, CMS-блоки.
- New/changed components: hero facts, четырёхчастная trust strip, тёмный header и hero.
- Variants and states: CTA активна только при наличии URL MAX; мобильное меню полноэкранное.

## Accessibility
- Target standard: WCAG AA для основного текста и CTA.
- Keyboard/focus behavior: видимый focus у ссылок и кнопок, Escape закрывает модальное фото.
- Contrast/readability: белый текст на графите, красный не используется для длинного текста.
- Reduced motion: анимации отключаются при пользовательском предпочтении.

## Responsive behavior
- Supported breakpoints/devices: 320px+; desktop 1024px+.
- Layout adaptations: фото Артёма первым на mobile, далее текст и CTA; карточки работ и отзывов листаются горизонтально.
- Touch/hover differences: крупные touch-targets не менее 48px, hover не обязателен для понимания.

## Interaction states
- Loading: показывается встроенный контент, пока CMS подгружается.
- Error: встроенный контент сохраняет работоспособность при недоступности API.
- Disabled: MAX CTA становится кнопкой без перехода только без URL бота.

## Content voice
- Tone: простой, деловой, личный.
- Terminology: «рассчитать», «подобрать проект», «реальные работы»; не обещать точную стоимость или срок без подтверждения.

## Implementation constraints
- Framework/styling system: Vite, vanilla JS, CSS, CMS API FastAPI.
- Performance constraints: eager только hero/фото производства; остальная галерея lazy.
- Test/screenshot expectations: Vite build, Python tests, desktop/mobile Playwright screenshot и проверка CTA.

## Open questions
- [ ] После подключения домена заменить временный `sslip.io` во внешних ссылках и webhook.
- [ ] При появлении подтверждённого среднего срока изготовления добавить его в trust strip через CMS.
