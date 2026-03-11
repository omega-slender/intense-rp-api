# 🎭 Intense RP API
**Intense RP** is an API with an intuitive visual interface that enables the unofficial integration of DeepSeek into SillyTavern.

![Preview](https://github.com/omega-slender/intense-rp-api/blob/main/images/Preview.gif)

> ⚠️ **This project is no longer maintained.**
>
> The new official version is hosted at [Intense RP NexT](https://github.com/LyubomirT/intense-rp-api-improvements), created by **LyubomirT** with my full authorization.
>
> 👉 It is the **official successor** of this project, and I highly recommend downloading and using it for future updates and support.


## 📋 Requirements
### 📦 For the Source Code
- 🐍 **Python**: Install from [python.org](https://www.python.org/).
- 📚 **Required Libraries**: `flask`, `waitress`, `customtkinter`, `selenium`, `seleniumbase`, `cryptography`, `webdriver-manager`, `packaging`, `beautifulsoup4`, `psutil` and `requests`.

### 🖥️ Windows Version
- ✅ No additional installations are required.

## ⚙️ How to Use
### 🚀 Intense RP API
1. 📥 Download the source code or the distributable version for Windows.
2. ▶️ Run `main.pyw` or `Intense RP API.exe`.
3. ⚙️ Click the **Settings** button.
4. 🌐 In **Browser**, select your preferred web browser.
5. ✉️ Enter your DeepSeek email and password in the **Email** and **Password** fields to log in automatically.
6. 🔥 Click the **Start** button and wait for the process to complete.
7. 📋 Once the API is active, copy the URL `http://127.0.0.1:5000/` or `YOUR-IP:5000/`.

## 🤖 SillyTavern
### 📥 Installation
1. Download **SillyTavern** from its official website [sillytavernai.com](https://sillytavernai.com/).

### 🔗 API Connections
1. Go to the [API Connections](https://github.com/omega-slender/intense-rp-api/blob/main/images/API%20Connections.png) section.
2. Under **Chat Completion Source**, select **Custom (OpenAI-compatible)**.
3. In the **Custom Endpoint (Base URL)** field, enter `http://127.0.0.1:5000/` or your personal IP.
4. Click **Connect**.

## ⚠️ Cloudflare Issues
If you're having trouble getting past **Cloudflare**, it's highly recommended to use **Google Chrome**, as it tends to be the most reliable browser for bypassing Cloudflare verification.

### 📌 Important information
- The **Main Prompt** must always include:
  - `DATA1: "{{char}}"`  
  - `DATA2: "{{user}}"`  

- In **Auxiliary Prompt**, you can use:
  - `{{max_tokens}}`  
  - `{{temperature}}`  

- To manually activate **DeepThink (R1)** or **Search** mode, simply include `{{r1}}` or `[r1]` in your message for DeepThink (R1), and `{{search}}` or `[search]` for Search.

## 🌐 Contact
Discover more about me and my projects on my [Linktree](https://linktr.ee/omega_slender).

## ☕ Support My Work
If you find this project useful and want to support its development, consider buying me a coffee in [Ko-fi](https://ko-fi.com/omega_slender)!  
