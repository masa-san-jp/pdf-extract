# pdf-extract

**PDF ファイルから「文字（テキスト）」だけを取り出すコマンドラインツール**です。
取り出したテキストは、要約・検索・コピペ・別ファイルへの保存などに使えます。

- 📄 パソコンの中にある PDF（ローカルファイル）
- ☁️ Google Drive にある PDF

の両方に対応しています。

---

## できること・できないこと

| こんなとき | できる？ |
|---|---|
| Word や Google ドキュメントから「PDF 書き出し」したファイルの文字を取り出す | ✅ できる |
| ダウンロードした資料 PDF・論文・請求書などの文字を取り出す | ✅ できる |
| Google Drive 上の PDF を、ダウンロードせずに直接読む | ✅ できる（初回だけ認証が必要） |
| **スキャナで紙を読み取っただけの PDF**（中身が画像だけ）の文字を取り出す | ❌ できない（OCR が必要で非対応） |

「文字データを持っている PDF」が対象です。スキャンや写真だけの PDF には文字データが無いので取り出せません。

---

## 必要なもの

- Python 3.8 以上
- Google Drive の PDF を読む場合：Google アカウントと `gcloud` CLI（[インストール手順](https://cloud.google.com/sdk/docs/install)）

---

## 最初の準備（初回だけ）

```bash
bash setup.sh
```

必要な部品（`pypdf` と Google API クライアント）を自動でインストールします。

- **パソコンの中の PDF だけ**なら、準備はこれで完了です。
- **Google Drive の PDF** も扱う場合は、もう 1 つ「認証（ログイン）」が必要です（下記参照）。

---

## 使い方（パソコンの中の PDF）

`/path/to/file.pdf` を実際の PDF の場所に置き換えてください。

```bash
./pdf_extract.py /path/to/file.pdf
```

> Mac なら、Finder の PDF をターミナルにドラッグ＆ドロップすると場所（フルパス）が自動入力されます。

`./pdf_extract.py` で動かない場合は、先頭に `python3` を付けてください。

```bash
python3 pdf_extract.py /path/to/file.pdf
```

### 実行結果

```
<!-- pdf-extract source -->
<!-- source: /path/to/file.pdf -->
<!-- name: file.pdf -->
<!-- mime: application/pdf -->
<!-- pages: 3/3 -->

（ここに本文テキストが出ます）
```

先頭の `<!-- ... -->` は「どのファイルか／何ページ取り出したか」のメモです。`pages: 3/3` は「全 3 ページ中 3 ページ分」を意味します。不要なら `--no-header` で消せます。

---

## オプション

オプションは PDF の場所の**後ろ**に付けます。組み合わせ可能です。

| やりたいこと | 付けるもの | 例 |
|---|---|---|
| 結果をファイルに保存する | `-o out.txt` | `./pdf_extract.py 資料.pdf -o 結果.txt` |
| 一部のページだけ取り出す | `--pages 1-5,8` | `./pdf_extract.py 資料.pdf --pages 1-5,8` |
| ページの区切りを入れる | `--page-markers` | `./pdf_extract.py 資料.pdf --page-markers` |
| 先頭のメモを消す | `--no-header` | `./pdf_extract.py 資料.pdf --no-header` |
| 入力をローカル/Drive に強制 | `--local` / `--drive` | `./pdf_extract.py 入力 --local` |

- **`--pages 1-5,8`** … 1〜5 ページと 8 ページだけ（ページ番号は 1 から数えます）。
- **`--page-markers`** … ページの境目に `--- page N ---` を入れます。

全部入りの例：

```bash
./pdf_extract.py 資料.pdf --pages 1-10 --page-markers -o 抜粋.txt
```

---

## Google Drive の PDF を読む

### 1. 初回だけ：ログイン（認証）

```bash
bash auth.sh
# 特定のアカウントを指定する場合：
bash auth.sh you@example.com
```

ブラウザが開くので Google アカウントでログインしてください。権限は「Drive を**読むだけ**」（`drive.readonly`）で、書き換え・削除はしません。

### 2. Drive のリンクか ID を渡す

```bash
./pdf_extract.py "https://drive.google.com/file/d/1AbC.../view"
```

> URL は記号が含まれることがあるので、ダブルクォート `"..."` で囲むと安全です。

リンクの取り出し方：Drive で PDF を右クリック →「リンクをコピー」。`/d/` と `/view` の間の長い文字列が「ファイル ID」です（ID だけ渡しても動きます）。

---

## うまくいかないとき（終了コード別）

| 番号 | 意味 | どうする？ |
|---|---|---|
| 0 | 成功 | 問題なし |
| 1 | 読み込み中のエラー | PDF が壊れている／通信不調。開き直す・再実行 |
| 2 | 入力のまちがい | パスのスペルミス・ファイル無し。入れ直す |
| 3 | 部品不足 or 未ログイン | ローカル → `bash setup.sh`／Drive → `bash auth.sh` |
| 4 | PDF じゃない | Drive のファイルが Google ドキュメント等。先に PDF へ書き出す |

### よくある質問

**日本語が「ςΩετ…」のように文字化けする**
その PDF が文字復元用の情報（ToUnicode マップ）を持っていない場合に起きます。Word・Google ドキュメント・Acrobat 製の PDF はほぼ問題ありません。化ける場合は別エンジンを足せます。

**何も出てこない／空っぽになる**
スキャン画像だけの PDF（文字データ無し）の可能性が高いです。OCR が必要で、このツールでは非対応です。

**`command not found` と出る**
実行権限が無いかもしれません。`python3 pdf_extract.py 資料.pdf` で実行してください。

---

## ライセンス

MIT — [LICENSE](LICENSE) を参照。
