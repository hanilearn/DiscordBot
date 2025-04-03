# DiscordBot

###### 事先準備

1. 申請Gemini API key

2. 建立discord機器人取得token並且邀請進入自己的discord帳號的伺服器中

3. 在電腦安裝python3

###### Discod後端

在.env檔中修改你自己的key和discord機器人token

```
DISCORD_TOKEN="你的discord_token"
GEMINI_API_KEY="你的API_KEY"
```
完成後執行ChatAIBot_Start.bat，自動腳本將建立python虛擬環境以及安裝相依套件，完成後執行後台腳本程式

###### 使用

進入自己的伺服器中輸入指令: /role 你好
成功的話，機器人會回覆你: 我會在你的DM中回答！
