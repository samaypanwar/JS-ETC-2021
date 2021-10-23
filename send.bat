echo OFF
set out_dir=%1
set in_dir=%2
set file=%3
scp -r "C:\Users\Samay Panwar\OneDrive - Nanyang Technological University\python files\projects\Resume Projects\JS-ETC-2021\%in_dir%\%path%" ubuntu@3.104.111.237:"/home/ubuntu/%out_dir%/%path%"