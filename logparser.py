import os
import re
import json

input_dir = 'logs'
output_dir = 'ParsedLogs'
os.makedirs(output_dir, exist_ok=True)

# Common log formats (feel free to expand this)
regex_patterns = [
    # Apache-style: [date time] [level] message
    re.compile(r"\[(?P<timestamp>.+?)\]\s+\[(?P<level>notice|warn|error|debug|info)\]\s+(?P<message>.+)", re.IGNORECASE),

    # Syslog-style: Dec 04 04:51:18 hostname app: message
    re.compile(r"(?P<timestamp>\w{3} \d{1,2} \d{2}:\d{2}:\d{2})\s+\S+\s+\S+: (?P<message>.+)", re.IGNORECASE),

    # ISO format with comma + CSV log style
    re.compile(r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*(?P<level>\w+),\s*(?P<message>.+)", re.IGNORECASE),

    # Nginx-style: 2024/07/29 04:51:18 [error] 1234#0: message
    re.compile(r"(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(?P<level>\w+)\] \d+#\d+: (?P<message>.+)", re.IGNORECASE),

    # Custom app: YYYY-MM-DDTHH:MM:SSZ [LEVEL] Message
    re.compile(r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+\[(?P<level>\w+)\]\s+(?P<message>.+)", re.IGNORECASE),

     re.compile(r"(?P<timestamp>\d{8}-\d{2}:\d{2}:\d{2}:\d{3})\|(?P<component>[^\|]+)\|(?P<id>\d+)\|(?P<message>.+)"),
]

def parse_log_line(line):
    for pattern in regex_patterns:
        match = pattern.match(line)
        if match:
            return {
                "timestamp": match.group("timestamp").strip(),
                "level": match.group("level").strip().lower() if 'level' in match.groupdict() else "info",
                "message": match.group("message").strip()
            }
    return None

def parse_log_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        parsed_count = 0
        skipped = 0

        for line in infile:
            parsed = parse_log_line(line)
            if parsed:
                outfile.write(json.dumps(parsed) + '\n')
                parsed_count += 1
            else:
                skipped += 1

        print(f"✅ {os.path.basename(input_path)} → Parsed: {parsed_count} | Skipped: {skipped}")

def parse_all_logs():
    log_files = [f for f in os.listdir(input_dir) if f.endswith('.log')]

    if not log_files:
        print("⚠️ No .log files found.")
        return

    for log_file in log_files:
        input_path = os.path.join(input_dir, log_file)
        output_file = os.path.splitext(log_file)[0] + '.jsonl'
        output_path = os.path.join(output_dir, output_file)

        parse_log_file(input_path, output_path)

    print(f"\n✅ All logs processed and saved in {output_dir}")

if __name__ == "__main__":
    parse_all_logs()
