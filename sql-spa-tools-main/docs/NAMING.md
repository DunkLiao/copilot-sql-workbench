# 命名規則

本專案由多個可直接在瀏覽器開啟的 SQL 工具頁面組成。所有工具頁面應遵循以下命名規則。

## 頁面名稱

頁面名稱統一使用以下格式：

```text
SQL SPA Tools｜功能名稱
```

同一個功能的瀏覽器分頁標題與頁面主標題應保持一致，皆使用 `SQL SPA Tools｜功能名稱` 作為主要名稱。版本號不放在頁面名稱中；若需補充其他必要資訊，放在名稱旁的說明文字中。

目前頁面名稱如下：

| 功能 | 頁面名稱 |
| --- | --- |
| 工具入口 | `SQL SPA Tools｜工具入口` |
| Oracle SQL 格式化 | `SQL SPA Tools｜Oracle SQL Formatter` |
| Oracle SQL 比對 | `SQL SPA Tools｜Oracle SQL Compare` |
| SQL 個資清除 | `SQL SPA Tools｜SQL 個資清除器` |
| SQL 檔案清冊 | `SQL SPA Tools｜SQL Catalog` |
| SQL 欄位血緣分析 | `SQL SPA Tools｜SQL 欄位血緣分析器` |
| SQLScriptManage | `SQL SPA Tools｜SQLScriptManage` |
| Excel／CSV 轉 SQL | `SQL SPA Tools｜Excel／CSV 轉 SQL` |
| Excel／CSV 轉 SQL CTE | `SQL SPA Tools｜Excel／CSV 轉 SQL CTE` |
| SQL Lab | `SQL SPA Tools｜SQL Lab` |
| 資料品質稽核中心 | `SQL SPA Tools｜資料品質稽核中心` |
| 資料關聯探索器 | `SQL SPA Tools｜資料關聯探索器` |
| SQL 欄位映射 | `SQL SPA Tools｜SQL 欄位映射` |

## HTML 檔名

HTML 檔名統一使用小寫 kebab-case，並以專案名稱 `sql-spa-tools-` 作為前綴：

```text
sql-spa-tools-<功能識別字>.html
```

`index.html` 是整個工具包的入口頁，為唯一不使用 `sql-spa-tools-` 前綴的保留檔名例外。入口頁仍須遵守頁面名稱與共用主題規範。

規則如下：

- 全部使用小寫英文字母。
- 單字之間使用半形連字號 `-`，不使用空白、底線或大寫字母。
- 檔名使用穩定、簡短且能辨識功能的英文識別字。
- 不在檔名中加入版本號、日期或狀態字樣。

目前檔名如下：

| 功能 | HTML 檔名 |
| --- | --- |
| Oracle SQL 格式化 | `sql-spa-tools-oracle-formatter.html` |
| Oracle SQL 比對 | `sql-spa-tools-sql-compare.html` |
| SQL 個資清除 | `sql-spa-tools-pii-cleaner.html` |
| SQL 檔案清冊 | `sql-spa-tools-catalog.html` |
| SQL 欄位血緣分析 | `sql-spa-tools-column-lineage.html` |
| SQLScriptManage | `sql-spa-tools-sqlscriptmanage.html` |
| Excel／CSV 轉 SQL | `sql-spa-tools-excel-csv-sql.html` |
| Excel／CSV 轉 SQL CTE | `sql-spa-tools-excel-csv-sql-cte.html` |
| SQL Lab | `sql-spa-tools-sql-lab.html` |
| 資料品質稽核中心 | `sql-spa-tools-data-quality-audit-center.html` |
| 資料關聯探索器 | `sql-spa-tools-data-relationship-explorer.html` |
| SQL 欄位映射 | `sql-spa-tools-schema-studio.html` |

## 新增頁面

新增工具頁面時，應同時完成以下項目：

1. 依規則命名 HTML 檔案。
2. 將 `<title>` 設為 `SQL SPA Tools｜功能名稱`。
3. 將頁面主標題設為相同的 `SQL SPA Tools｜功能名稱`。
4. 不在頁面名稱、檔名或主標題中加入版本號。
5. 若功能頁面被其他文件或索引引用，建立檔案後同步更新引用路徑。

## 頁面導覽

`index.html` 是工具包入口頁。所有工具頁面都必須提供回首頁連結，統一使用：

```html
<a class="home-link" href="index.html">⌂ 工具入口</a>
```

入口頁本身不需要連結回自己；若新增工具頁，必須同步將其加入 `index.html` 的工具清單。
