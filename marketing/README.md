# Маркетинговая программа ShadowSecurityScanner

Цель: **adoption**, то есть рост загрузок, звёзд и узнаваемости бесплатного сканера.
Денег программа не требует: каналы бесплатные, контент строится на открытых данных и
на коде, который уже есть.

## Исходная точка (12.10.2026)

| Метрика | Значение |
|---|---|
| Звёзды на GitHub | 11 (8 из них за последние 2 недели) |
| Загрузки, всего | 672: Windows 427 · Linux 172 · macOS 73 |
| Загрузки последнего релиза | ~60–90 за неделю (v1.5.4: 61, v1.5.6: 87) |
| Просмотры репозитория | ~120–160 в неделю |
| Источники трафика | Bing, DuckDuckGo, Google, alternativeto.net, chatgpt.com |
| Show HN / Reddit / awesome-списки | не было |

## Цели на 90 дней (к 15.01.2027)

| KPI | Цель | Откуда берётся |
|---|---|---|
| Звёзды | 150+ | Show HN + Reddit + awesome-списки (разовые всплески) |
| Загрузки в неделю | 200+ | всплески от запуска и постоянный поток из поиска и KEV-дайджеста |
| Страниц сайта в индексе Google | 25+ | KEV-дайджест добавляет страницу каждую неделю |
| Упоминание в ответах ChatGPT/Perplexity на «free Nessus alternative» | да | Reddit/HN-упоминания, llms.txt, страницы сравнения |

Метрики собираются автоматически; каждый понедельник создаётся issue с отчётом
(метка `marketing-report`).

---

## Как устроена автоматика

Workflow [`.github/workflows/marketing.yml`](../.github/workflows/marketing.yml) запускается каждые
3 часа; [`run.py`](run.py) сам решает, что пора делать:

| Задача | Когда | Что делает |
|---|---|---|
| `release` | каждый запуск | Новый релиз в `safetylab/ShadowSecurityScanner`, и сразу: версия в JSON-LD главной, `llms.txt`, страница [/changelog/](https://shadowsecurityscanner.com/changelog/), sitemap, анонс в соцсети |
| `metrics` | раз в день | Звёзды, загрузки по ОС, трафик репозитория (GitHub хранит его всего 14 дней, здесь копится вся история), опционально статистика сайта из Cloudflare |
| `mentions` | раз в день | HN, Stack Exchange, Reddit, GitHub: упоминания проекта и обсуждения, где уместен ответ, сводятся в issue `marketing-mentions` |
| `devto` | раз в 14 дней, вт–чт | Следующая статья из [`articles/`](../articles/) публикуется на dev.to со ссылками на сайт, плюс анонс |
| `kev` | понедельник | Страница [/kev/&lt;неделя&gt;/](https://shadowsecurityscanner.com/kev/): новые CVE из CISA KEV с EPSS, наличием эксплойтов, ransomware, сроками CISA и отметкой, есть ли у сканера активная проверка. Плюс анонс |
| `report` | понедельник | Недельный отчёт в issue |

После генерации изменённые страницы деплоятся ([`deploy.yml`](../.github/workflows/deploy.yml)), а
очередь постов уходит в соцсети ([`post.py`](post.py)), только по будням с 12 до 21 UTC.

**KEV-дайджест — основной контентный двигатель.** Каждую неделю появляется новая страница
с фактами из открытых источников (CISA, FIRST.org, Exploit-DB, Metasploit), без
сгенерированного текста. Она ловит запросы вида «CVE-XXXX-YYYY exploited» и даёт повод для
поста каждую неделю, и каждый пост ведёт к сканеру.

Тексты не генерируются языковой моделью: в security-аудитории одна выдуманная деталь про
CVE стоит дороже десятка постов.

### Ручной запуск

Actions → *Marketing automation* → *Run workflow*: в `tasks` можно указать, например,
`kev report`, а `force_post` игнорирует окно публикаций. Локально:

```bash
cd marketing
GITHUB_TOKEN=$(gh auth token) python3 run.py release kev   # сгенерировать страницы
DRY_RUN=1 python3 post.py                                  # показать тексты постов, ничего не отправлять
python3 kev_digest.py 2026-W38                             # бэкфилл дайджеста за прошлую неделю (без поста)
```

---

## Настройка (один раз)

### 1. Чтобы автодеплой реально доходил до shadowsecurityscanner.com

Сейчас домен через Cloudflare смотрит на Apache (5.78.116.238), куда файлы заливаются
руками, а GitHub Pages параллельно отдаёт дубль сайта на `andriigordiienko.github.io`.
Выбери один вариант:

- **A. Перевести сайт на GitHub Pages (рекомендую).** Repo → Settings → Pages → Custom
  domain = `shadowsecurityscanner.com`, затем в Cloudflare DNS заменить A-запись на
  `CNAME shadowsecurityscanner.com → andriigordiienko.github.io`. Когда сертификат
  выпустится, включить *Enforce HTTPS*. Каждый деплой сразу оказывается на домене, а дубль
  на github.io начинает делать 301-редирект на домен. Сервер для сайта больше не нужен.
- **B. Оставить Apache.** Добавить секреты `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_PATH`,
  `DEPLOY_SSH_KEY` (приватный ключ отдельного deploy-пользователя) и `DEPLOY_KNOWN_HOSTS`
  (вывод `ssh-keyscan 5.78.116.238`). Деплой зальёт файлы через rsync, ничего не удаляя.
  SSH на сервере должен быть доступен с IP-адресов GitHub Actions. Дубль на github.io
  останется, его закрывают canonical-теги.

### 2. Секреты (Settings → Secrets and variables → Actions)

Канал без секретов просто пропускается, поэтому каналы можно подключать по одному.

| Секрет | Где взять |
|---|---|
| `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` | bsky.app → Settings → Privacy and security → App passwords |
| `MASTODON_INSTANCE`, `MASTODON_TOKEN` | Аккаунт на `https://infosec.exchange` (самая живая security-площадка) → Preferences → Development → New application, scope `write:statuses` → *Your access token* |
| `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET` | developer.x.com → проект и приложение, *User authentication settings*: Read and write → Keys and tokens. Бесплатного тарифа хватает на ~500 постов в месяц, но лимиты лучше перепроверить |
| `LINKEDIN_TOKEN`, `LINKEDIN_AUTHOR` | linkedin.com/developers → приложение с продуктами *Share on LinkedIn* и *Sign In with LinkedIn using OpenID Connect* → OAuth token tool со scope `w_member_social openid profile`. `LINKEDIN_AUTHOR` = `urn:li:person:<sub>`, где `sub` берётся из `GET https://api.linkedin.com/v2/userinfo`. **Токен живёт 60 дней**: недельный отчёт покажет ошибку канала, когда его пора обновить |
| `DEVTO_API_KEY` | dev.to → Settings → Extensions → DEV Community API Keys |
| `METRICS_TOKEN` | Fine-grained PAT: владелец `safetylab`, репозиторий `ShadowSecurityScanner`, *Administration: Read-only*. Нужен для трафика: без него собираются только звёзды и загрузки |
| `CF_API_TOKEN`, `CF_ZONE_ID` | Cloudflare → My Profile → API Tokens → токен с *Zone → Analytics → Read*; Zone ID есть на Overview домена. Даёт просмотры сайта без трекеров на страницах |
| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` | reddit.com/prefs/apps → *create app* → тип *script*. Без них Reddit почти всегда отвечает 429 |

### 3. Сделать в SSS-репозитории

В `andriigordiienko/SSS` нужен коммит с `scripts/release-notes.sh` и правкой
`.github/workflows/release.yml`. После этого у каждого тега на GitHub будет настоящий
changelog из `feat` / `fix` / `perf`-коммитов вместо «Automated build of vX». Из него
собирается /changelog/ и пункт «What's new» в анонсах.

---

## Ручная часть: запуск (6 недель)

Автоматика держит постоянный поток, но рост звёзд дают разовые запуски, а их делает
человек. Reddit и HN запрещают автопостинг и банят за него, поэтому эти площадки только
вручную. Готовые тексты лежат в [`off-page-seo-kit.md`](../off-page-seo-kit.md).

| Неделя | Действие |
|---|---|
| 1 (13–19.10) | Search Console + Bing Webmaster (метатеги уже стоят) → отправить sitemap. Выбрать вариант деплоя из п. 1. Завести Bluesky, Mastodon и dev.to, добавить секреты. AlternativeTo: добавить как альтернативу Nessus/OpenVAS/Nexpose |
| 2 (20–26.10) | **Show HN** во вт–чт около 09:00 ET, 2 часа отвечать на каждый комментарий. До этого заменить CSS-мокапы на главной на реальные скриншоты (`assets/screenshot-*.png` уже есть) |
| 3 (27.10–2.11) | Reddit: r/netsec (только через техническую статью, например про EPSS/KEV), r/cybersecurity, r/sysadmin, r/homelab. Не больше одной площадки в день, начинать с пользы, а не с питча |
| 4 (3–9.11) | PR в `enaqx/awesome-pentest`, `sbilly/awesome-security`, `Hack-with-Github/Awesome-Hacking`. Product Hunt (вт, 00:01 PT) |
| 5 (10–16.11) | YouTube: демо на 2–3 минуты (скан → «Most exploited» → diff → SARIF), встроить на главную с `VideoObject` |
| 6 (17–23.11) | Подвести итоги по отчётам, удвоить то, что дало загрузки |

## Ручная часть: еженедельный ритм (~1 час)

- **Понедельник:** прочитать отчёт-issue, сделать репост KEV-дайджеста в LinkedIn с личным
  комментарием (такие посты набирают в разы больше охвата, чем автопост).
- **Каждый день по 5 минут:** issue `marketing-mentions` → ответить по существу в 1–2
  обсуждениях. Инструмент упоминать только там, где он действительно решает вопрос.
- **Раз в 2 недели:** положить новую статью в `articles/NN-*.md` (формат front matter как у
  существующих, `published: false`), dev.to-задача опубликует её сама. Темы: «EPSS vs CVSS на
  реальных данных KEV за квартал», «Nessus Essentials 16 IP: что дальше», «SARIF из сканера
  в GitHub code scanning».
- **Каждый релиз:** ничего делать не нужно. Если релиз большой, можно добавить пост на Reddit/HN
  о самой интересной фиче.

## Что важно помнить

- Репозиторий сайта публичный, и `marketing/data/` (метрики, трафик, упоминания) тоже видно.
  Для open-source-проекта это нормально, но учитывай это.
- Если пост не ушёл в какой-то канал, следующий запуск повторяет его до 3 раз, после чего
  пост уходит в `data/sent/` с полем `errors`. Ошибки каналов видны в недельном отчёте.
- Анонс релиза старше 7 дней не публикуется: при включении автоматики старые релизы не
  посыпятся в ленту.
