# pdf-extract

## 日本語

**PDF ファイルから「文字（テキスト）」だけを取り出すコマンドラインツール**です。
取り出したテキストは、要約・検索・コピペ・別ファイルへの保存などに使えます。

- パソコンの中にある PDF（ローカルファイル）
- Google Drive にある PDF

の両方に対応しています。

---

### できること・できないこと

| こんなとき | できる？ |
|---|---|
| Word や Google ドキュメントから「PDF 書き出し」したファイルの文字を取り出す | できる |
| ダウンロードした資料 PDF・論文・請求書などの文字を取り出す | できる |
| Google Drive 上の PDF を、ダウンロードせずに直接読む | できる（初回だけ認証が必要） |
| **スキャナで紙を読み取っただけの PDF**（中身が画像だけ）の文字を取り出す | できない（OCR が必要で非対応） |

「文字データを持っている PDF」が対象です。スキャンや写真だけの PDF には文字データが無いので取り出せません。

---

### 必要なもの

- Python 3.8 以上
- Google Drive の PDF を読む場合：Google アカウントと `gcloud` CLI（[インストール手順](https://cloud.google.com/sdk/docs/install)）

---

### 最初の準備（初回だけ）

```bash
bash setup.sh
```

必要な部品（`pypdf` と Google API クライアント）を自動でインストールします。

- **パソコンの中の PDF だけ**なら、準備はこれで完了です。
- **Google Drive の PDF** も扱う場合は、もう 1 つ「認証（ログイン）」が必要です（下記参照）。

---

### 使い方（パソコンの中の PDF）

`/path/to/file.pdf` を実際の PDF の場所に置き換えてください。

```bash
./pdf_extract.py /path/to/file.pdf
```

> Mac なら、Finder の PDF をターミナルにドラッグ＆ドロップすると場所（フルパス）が自動入力されます。

`./pdf_extract.py` で動かない場合は、先頭に `python3` を付けてください。

```bash
python3 pdf_extract.py /path/to/file.pdf
```

#### 実行結果

```text
<!-- pdf-extract source -->
<!-- source: /path/to/file.pdf -->
<!-- name: file.pdf -->
<!-- mime: application/pdf -->
<!-- pages: 3/3 -->

（ここに本文テキストが出ます）
```

先頭の `<!-- ... -->` は「どのファイルか／何ページ取り出したか」のメモです。`pages: 3/3` は「全 3 ページ中 3 ページ分」を意味します。不要なら `--no-header` で消せます。

---

### オプション

オプションは PDF の場所の**後ろ**に付けます。組み合わせ可能です。

| やりたいこと | 付けるもの | 例 |
|---|---|---|
| 結果をファイルに保存する | `-o out.txt` | `./pdf_extract.py 資料.pdf -o 結果.txt` |
| 一部のページだけ取り出す | `--pages 1-5,8` | `./pdf_extract.py 資料.pdf --pages 1-5,8` |
| ページの区切りを入れる | `--page-markers` | `./pdf_extract.py 資料.pdf --page-markers` |
| 先頭のメモを消す | `--no-header` | `./pdf_extract.py 資料.pdf --no-header` |
| 入力をローカル/Drive に強制 | `--local` / `--drive` | `./pdf_extract.py 入力 --local` |

- **`--pages 1-5,8`**: 1〜5 ページと 8 ページだけ（ページ番号は 1 から数えます）。
- **`--page-markers`**: ページの境目に `--- page N ---` を入れます。

全部入りの例：

```bash
./pdf_extract.py 資料.pdf --pages 1-10 --page-markers -o 抜粋.txt
```

---

### Google Drive の PDF を読む

#### 1. 初回だけ：ログイン（認証）

```bash
bash auth.sh
# 特定のアカウントを指定する場合：
bash auth.sh you@example.com
```

ブラウザが開くので Google アカウントでログインしてください。権限は「Drive を**読むだけ**」（`drive.readonly`）で、書き換え・削除はしません。

#### 2. Drive のリンクか ID を渡す

```bash
./pdf_extract.py "https://drive.google.com/file/d/1AbC.../view"
```

> URL は記号が含まれることがあるので、ダブルクォート `"..."` で囲むと安全です。

リンクの取り出し方：Drive で PDF を右クリック →「リンクをコピー」。`/d/` と `/view` の間の長い文字列が「ファイル ID」です（ID だけ渡しても動きます）。

---

### うまくいかないとき（終了コード別）

| 番号 | 意味 | どうする？ |
|---|---|---|
| 0 | 成功 | 問題なし |
| 1 | 読み込み中のエラー | PDF が壊れている／通信不調。開き直す・再実行 |
| 2 | 入力のまちがい | パスのスペルミス・ファイル無し。入れ直す |
| 3 | 部品不足 or 未ログイン | ローカル → `bash setup.sh`／Drive → `bash auth.sh` |
| 4 | PDF じゃない | Drive のファイルが Google ドキュメント等。先に PDF へ書き出す |

#### よくある質問

**日本語が「ςΩετ…」のように文字化けする**

その PDF が文字復元用の情報（ToUnicode マップ）を持っていない場合に起きます。Word・Google ドキュメント・Acrobat 製の PDF はほぼ問題ありません。化ける場合は別エンジンを足せます。

**何も出てこない／空っぽになる**

スキャン画像だけの PDF（文字データ無し）の可能性が高いです。OCR が必要で、このツールでは非対応です。

**`command not found` と出る**

実行権限が無いかもしれません。`python3 pdf_extract.py 資料.pdf` で実行してください。

---

### ライセンス

MIT — [LICENSE](LICENSE) を参照。

---

## English

**A small command-line tool that extracts plain text from PDF files.**
The extracted text can be used for summarizing, searching, copy-pasting, or saving to another file.

It works with both:

- PDFs on your computer (local files)
- PDFs stored in Google Drive

---

### What it can and can't do

| Situation | Supported? |
|---|---|
| Extract text from a PDF exported from Word / Google Docs | Yes |
| Extract text from a downloaded report / paper / invoice PDF | Yes |
| Read a PDF in Google Drive directly (without downloading it first) | Yes (one-time auth required) |
| Extract text from a **scanned** PDF (image-only, no text layer) | No (OCR needed, out of scope) |

This tool works with PDFs that contain a real text layer. Scanned or photographed
PDFs have no text data, so nothing can be extracted from them here.

---

### Requirements

- Python 3.8+
- For Google Drive PDFs: a Google account and the `gcloud` CLI ([install guide](https://cloud.google.com/sdk/docs/install))

---

### Setup (first time only)

```bash
bash setup.sh
```

This installs the Python dependencies (`pypdf` and the Google API client).

- For **local PDFs only**, that's all you need.
- For **Google Drive PDFs**, you also need to authenticate once. See
  "Reading PDFs from Google Drive" below.

---

### Usage: local PDF

```bash
./pdf_extract.py /path/to/file.pdf
```

> On macOS, you can drag a PDF from Finder into the terminal to fill in its full path.

If `./pdf_extract.py` doesn't run, call it through Python directly:

```bash
python3 pdf_extract.py /path/to/file.pdf
```

#### What you get

```text
<!-- pdf-extract source -->
<!-- source: /path/to/file.pdf -->
<!-- name: file.pdf -->
<!-- mime: application/pdf -->
<!-- pages: 3/3 -->

(the extracted text appears here)
```

The leading `<!-- ... -->` block is a small metadata header (which file, how many
pages). `pages: 3/3` means "3 of 3 pages were extracted". Use `--no-header` to omit it.

---

### Options

Options go **after** the input. They can be combined.

| Goal | Flag | Example |
|---|---|---|
| Save the result to a file | `-o out.txt` | `./pdf_extract.py file.pdf -o out.txt` |
| Extract only some pages | `--pages 1-5,8` | `./pdf_extract.py file.pdf --pages 1-5,8` |
| Insert page separators | `--page-markers` | `./pdf_extract.py file.pdf --page-markers` |
| Omit the metadata header | `--no-header` | `./pdf_extract.py file.pdf --no-header` |
| Force local-file input | `--local` | `./pdf_extract.py input --local` |
| Force Drive input | `--drive` | `./pdf_extract.py input --drive` |

- **`--pages 1-5,8`**: extracts pages 1-5 and page 8 (page numbers are 1-based).
- **`--page-markers`**: inserts `--- page N ---` between pages so you can tell which
  page text came from.

Full example:

```bash
./pdf_extract.py report.pdf --pages 1-10 --page-markers -o excerpt.txt
```

---

### Reading PDFs from Google Drive

#### 1. Authenticate (first time only)

```bash
bash auth.sh
# or for a specific account:
bash auth.sh you@example.com
```

A browser opens; sign in with your Google account. This grants **read-only**
access to Drive (`drive.readonly`). The tool never modifies or deletes anything.

#### 2. Pass the Drive link or file ID

```bash
./pdf_extract.py "https://drive.google.com/file/d/1AbC.../view"
```

> Wrap the URL in double quotes `"..."` so special characters don't break the command.

To get the link: right-click the PDF in Google Drive -> **Copy link** (or **Share ->
Copy link**). The long string between `/d/` and `/view` is the file ID; passing just
the ID works too.

---

### Troubleshooting (by exit code)

The tool prints an exit code when it finishes. Match it against this table:

| Code | Meaning | What to do |
|---|---|---|
| 0 | Success | Nothing. It worked |
| 1 | Runtime / API error | The PDF may be corrupt, or the network failed. Reopen the file / retry |
| 2 | Bad input | Wrong path, or file not found. Re-enter the path |
| 3 | Missing dependency or not authenticated | Local PDF -> run `bash setup.sh`; Drive PDF -> run `bash auth.sh` |
| 4 | Not a PDF | The Drive file is a native Google Doc/Sheet/Slide. Export it to PDF first |

#### FAQ

**Japanese (or other non-Latin) text comes out garbled**

This happens when a PDF lacks the mapping information (a *ToUnicode* map) needed to
recover characters. PDFs produced by Word, Google Docs, or Acrobat are almost always
fine. A different extraction engine can be added if you hit a PDF that garbles.

**No text comes out / the result is empty**

The PDF is probably scanned (image-only) with no text data. Extracting text from it
requires OCR, which this tool does not do.

**`command not found`**

The file may not be executable. Run it through Python instead:
`python3 pdf_extract.py file.pdf`

---

### How input is detected

| Input | Treated as |
|---|---|
| An existing path (e.g. `/Users/you/...`) | Local PDF |
| A `https://.../d/<ID>/...` URL | Drive PDF |
| A long ID-like string with no matching local file | Drive PDF |

If detection guesses wrong, force it with `--local` or `--drive`.

---

### License

MIT. See [LICENSE](LICENSE).
