# ERP 进销存系统 - 网页版 (v1.0)

基于你原来的 Django 项目重新打造的**全新网页版 ERP 系统**。

## ✨ 特点

- 完全网页操作（无需安装任何软件）
- MacBook M1 Pro 完美支持
- 一键启动（Docker）
- 实时库存更新
- 简洁现代界面（Tailwind CSS）
- 包含示例数据，开箱即用

## 🚀 快速开始（推荐方式）

### 方法一：使用 Docker（最简单，推荐）

1. 确保已安装 **Docker Desktop**（Mac 版）
2. 在项目文件夹中打开终端，执行：
   ```bash
   docker compose up --build
   ```
3. 浏览器打开：**http://localhost:5000**

### 方法二：本地 Python 运行

```bash
pip install -r requirements.txt
python app.py
```

## 📋 功能模块

- **数据看板**：总览产品数、库存量、预警、低库存提醒
- **产品管理**：添加/查看产品
- **库存查询**：实时库存 + 价值统计
- **入库管理**：新增入库 + 自动增加库存
- **出库管理**：新增出库 + 自动扣减库存（防超卖）

## 📁 项目结构

```
erp-web/
├── app.py              # 主程序
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── templates/          # 网页界面
│   ├── base.html
│   ├── dashboard.html
│   ├── products.html
│   ├── stock.html
│   ├── inbound.html
│   └── outbound.html
└── instance/           # 数据库（自动生成）
```

## 🔄 下一步迭代

这个是 **MVP 版本**（最小可用产品）。

你测试后告诉我：
- 想加什么功能？（客户管理、报表导出、用户权限、供应商等）
- 哪个页面不好用？
- 需要修改什么？

我马上改代码 → 推到 GitHub → 你 `git pull` 更新。

---

**你的 MacBook M1 Pro 已经准备好了！**

现在就开始测试吧～ 有任何问题随时告诉我！