@echo off
@REM python "%~dp0generate_episodes_json.py" --folder "d:\NC_Data\Documents\012_UOL_Podcasts\CM3035"
@REM python "%~dp0generate_podcast_rss.py" ^
@REM   --folder "d:\NC_Data\Documents\012_UOL_Podcasts\CM3035" ^
@REM   --base-url "https://nextcloud.mnaumann.com/s/HPSz3SAtzDdKqmW/download" ^
@REM   --output "d:\NC_Data\Documents\012_UOL_Podcasts\CM3035\podcast.rss" ^
@REM   --title "CM3035 Podcast"
.venv\Scripts\python.exe generate_podcast_rss.py ^
  --folder "d:\NC_Data\Documents\012_UOL_Podcasts\CM3035" ^
  --base-url "https://nextcloud.mnaumann.com/s/HPSz3SAtzDdKqmW/download" ^
  --output "d:\NC_Data\Documents\012_UOL_Podcasts\CM3035\podcast.rss" ^
  --title "CM3035 Podcast"
