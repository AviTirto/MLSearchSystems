import srt
import os
from dotenv import load_dotenv

load_dotenv()

class Parser():
    def __init__(self, **kwargs):
        self.srt_dir = kwargs.get('srt_dir', None)
        if self.srt_dir:
            self.srt_files = [self.srt_dir + '/' + file for file in os.listdir(self.srt_dir)]
    
    def format_timedelta(self, td):
        """Convert timedelta to HH:MM:SS format."""
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def parse_chunks(self, srt_file_name):
        with open(srt_file_name, 'r') as f:
            data = f.read()
            subtitles = list(srt.parse(data))  # Convert generator to list

            results = []
            content = ""
            start_time = None

            for s in subtitles:
                content += s.content
                if s.index % 16 == 0:
                    if start_time is None:
                        start_time = s.start

                    results.append({
                        "index": len(results) + 1,
                        "content": content,
                        "start_time": self.format_timedelta(start_time),
                        "end_time": self.format_timedelta(s.end),
                        "seconds": start_time.total_seconds()
                    })

                    # Update start_time for the next block
                    start_time = s.end
                    content = ""

            # If there's any remaining content after the loop
            if content:
                results.append({
                    "index": len(results) + 1,
                    "content": content,
                    "start_time": self.format_timedelta(start_time) if start_time else None,
                    "end_time": "-",
                    "seconds": start_time.total_seconds() if start_time else None
                })
            
            return results