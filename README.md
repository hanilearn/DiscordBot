# DiscordBot

### 事先準備

1. 申請Gemini API key
   https://aistudio.google.com/apikey

3. 建立discord機器人取得token並且邀請進入自己的discord帳號的伺服器中  
   https://discord.com/developers/applications/  
   新建機器人->取個名字->進入Bot分頁->勾選 Server Members Intent & Message Content Intent->按reset token 獲得token  
   ->進入OAuth2分頁->勾選 bot開出其他權限->勾選 send message & Read Message history->最底下獲得一器人邀請網址，貼到瀏覽器網址列就能邀請機器人到伺服器中  

5. 在電腦安裝python3
   https://www.python.org/downloads/

### Discod後端

在.env檔中修改你自己的key和discord機器人token

```
DISCORD_TOKEN="你的discord_token"
GEMINI_API_KEY="你的API_KEY"
```
完成後執行ChatAIBot_Start.bat，自動腳本將建立python虛擬環境以及安裝相依套件，完成後執行後台腳本程式

### 使用

進入自己的伺服器中輸入指令: /role 你好  
成功的話，機器人會回覆你: 我會在你的DM中回答！  
進入DM中可以直接與機器人AI對話  
