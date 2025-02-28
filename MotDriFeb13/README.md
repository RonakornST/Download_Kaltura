## Merge all of .ts to single .mp4
```
ls segment_*.ts | sort -V | awk '{print "file '\''" $0 "'\''"}' > file_list.txt
```

```
ffmpeg -f concat -safe 0 -i file_list.txt -c copy final_video.mp4
```
