![](https://img.shields.io/badge/状態-リリース-blue)
![](https://img.shields.io/badge/build-passing-green)


## プロジェクト名

MeetingHelper ver.2

<!-- プロジェクトについて -->

## プロジェクトについて

大学内コミュニティの定期ミーティングの準備（出欠席管理・グループ分け等）をLINE上で完結できるシステム<br>

紐づけられたLINE公式アカウントから機能を利用でき、管理者用のアクセスサイトも作成した<br>
以前[試験的に開発したver.1](https://github.com/Integral-07/MeetingHelper_ver1)からの変更点
<ul>
  <li>フレームワークの刷新</li>
  <li>データベースの永続化</li>
  <li>応答速度の高速化</li>
  <li>管理者用アクセスサイトの作成</li>
</ul>
  <p align="left">
    <br />
    <a href="#"><strong>プロジェクト詳細（Qiita記事） »</strong></a>
    <br>
    <br>
    <a href="https://www.dropbox.com/scl/fi/m1zdvxrh41585sv96a2ei/_.pdf?rlkey=9zas2mep4rbjyrrmgeq8esq1b&st=ezwbke97&dl=0"><strong>MeetingHelper(部会ヘルパ)説明書 »</strong></a>
    <br />
    <br />

## 使用技術一覧

<!-- シールド一覧 -->
<p style="display: inline">
  <!-- フロントエンドのフレームワーク -->
  <img src="https://img.shields.io/badge/-LINE MessagingAPI-C0C300.svg?logo=line&style=for-the-badge">
  <!-- バックエンドのフレームワーク -->
  <img src="https://img.shields.io/badge/-Django-092E20.svg?logo=django&style=for-the-badge">
  <!-- バックエンドの言語 -->
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
  <!-- ミドルウェア -->
  <img src="https://img.shields.io/badge/-Postgresql-336791.svg?logo=postgresql&style=for-the-badge">
  <!-- インフラ -->
  <img src="https://img.shields.io/badge/-Docker-1488C6.svg?logo=docker&style=for-the-badge">
</p>


## 環境

| 言語・フレームワーク    | バージョン  |
| --------------------- | ---------- |
| Python                | mcr.microsoft.com/devcontainers/python:1-3.12-bullseye     |
| Django                | 4.2.0      |
| PostgreSQL            | 2.9.10     |

その他のパッケージのバージョンは requirements.lock を参照してください
