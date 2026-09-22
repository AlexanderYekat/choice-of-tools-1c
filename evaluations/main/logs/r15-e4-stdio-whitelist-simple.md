# r15 E4 — stdio `[tools].enabled` и связка `--path` + `--config` — 2026-09-22

Binary: `C:\Users\Enduro\Documents\1c\Tools\bsl-indexer\bsl-indexer.exe`
Isolated `CODE_INDEX_HOME`: `.v8/work/r15-stdio-whitelist/home`.
Dump: `source-checkouts/simple1CAiConf`. Демон запускался/останавливался
трижды в рамках прогонов; дамп не редактировался.

## Что проверялось

`serve --help` предупреждает: `"Если указан и --path — CLI-пути имеют
приоритет и конфиг игнорируется"`. Раньше `[tools].enabled` проверялся
только на HTTP без `--path`. Открытыми оставались: то же самое на
stdio-транспорте, и что именно означает «конфиг игнорируется» — весь файл
или только секцию `[[paths]]`.

## Результат

**1. `[tools].enabled` на stdio без `--path` работает так же, как на
HTTP.** `serve --transport stdio --config daemon.toml` (whitelist из 9
имён + опечатка `not_a_real_tool`): `tools/list` вернул ровно 9 имён;
вызов `grep_code` (не в списке) отказан `-32602`
`"tool 'grep_code' is disabled by [tools].enabled whitelist in
daemon.toml"` — идентично HTTP-прогону.

**2. `--path` действительно замещает `[[paths]]` из конфига целиком, а не
просто «предпочитается» при конфликте.** Тест с сознательно РАЗНЫМ
alias'ом: конфиг объявляет `alias = "simple"`, CLI получает
`--path other=<тот же дамп>`. Результат:
`repo=simple` → `{"status":"unknown_repo","message":"Неизвестный repo
'simple'. Доступные: [\"other\"]. ..."}` — alias из конфига **не
существует вообще**, доступен только `"other"` из `--path`. Это
подтверждает предупреждение `--help` буквально для секции `[[paths]]`.

**3. Но `[tools].enabled` из ТОГО ЖЕ конфига продолжает действовать, даже
когда `--path` присутствует.** В сессии с `--config` + `--path` (тем же
alias, что и в конфиге, `simple`) `tools/list` всё равно вернул ровно 9
whitelisted имён, и `grep_code` всё равно был отказан whitelist'ом — **не**
полный список инструментов, как можно было бы ожидать, если бы «конфиг
игнорируется» относилось ко всему файлу.

**Вывод: формулировка `--help` вводит в заблуждение.** `--path` замещает
только секцию `[[paths]]` (репозитории/алиасы); секция `[tools]`
(whitelist) из того же `--config` **продолжает применяться** независимо от
присутствия `--path`. Кто использует `--path` для смены репозитория на
лету, не теряет защиту whitelist'а — но и не может рассчитывать, что
алиасы из конфига останутся доступны.

**Побочное наблюдение.** Демон (`daemon run`) индексирует по
`[[paths]]` из `daemon.toml` **на момент старта демона**, независимо от
того, что отдельные `serve`-сессии потом передают через `--path`. Разные
`--path` у клиентских stdio-сессий управляют тем, какие алиасы видны
именно ЭТОЙ сессии, а не тем, что демон индексирует.

## Таблица

| # | Сценарий | Транспорт | `tools/list` | `grep_code` | Alias конфига (`simple`) |
|---|---|---|---|---|---|
| 1 | `--config` (whitelist 9) | stdio | 9/9, совпадает | отказан whitelist'ом | доступен |
| 2 | `--config` + `--path other=...` (whitelist 9, другой alias) | stdio | 9/9, whitelist сохранён | отказан whitelist'ом | **недоступен** — `unknown_repo`, доступен только `other` |

Raw JSON: `r15-mcp-stdio-whitelist-session-a.json`,
`r15-mcp-stdio-whitelist-session-b.json`,
`r15-mcp-stdio-path-override-followup.json`,
`r15-mcp-stdio-whitelist-simple.json`,
`r15-mcp-stdio-path-override-followup-checks.json`.
