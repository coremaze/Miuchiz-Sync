# Miuchiz-Sync
The server can currently get Miuchiz Sync to go entirely through its logging in process, it can not get it to log off.

There is a byte responsible for logging Miuchiz Sync off at ["miuchiz sync.exe" + 0x7C34] + 0x4824. Changing it to 1 while Miuchiz Sync is logged in will cause it to start downloading and saving character data to the handheld.

The server is able to send character data back to Miuchiz Sync, and some values (creditz, happiness, hunger, and boredom) are known and can be changed.
