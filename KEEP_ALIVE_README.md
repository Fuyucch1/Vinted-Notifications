# Keep-Alive Component for Vinted Notifications

This component prevents free hosting platforms (like Render, Heroku, Railway, etc.) from shutting down your Vinted Notifications application due to inactivity.

## How It Works

The keep-alive service runs in a background thread and periodically sends HTTP requests to your application's web interface. This simulates user activity and prevents hosting platforms from putting your app to sleep.

## Features

- **Automatic Ping**: Sends periodic HTTP requests to keep the app active
- **Configurable Interval**: Set ping frequency from 60 seconds to 1 hour
- **Error Handling**: Robust retry logic with exponential backoff
- **Status Monitoring**: Real-time status display in the web UI
- **Thread-Safe**: Runs in a separate daemon thread
- **Graceful Shutdown**: Properly stops when the application shuts down

## Configuration

### Via Web UI

1. Navigate to the **Configuration** page in your web interface
2. Find the **Keep-Alive Service** section
3. Enable the service using the toggle switch
4. Set your preferred ping interval (default: 300 seconds / 5 minutes)
5. Click **Save All Settings**

### Configuration Options

- **Enable Keep-Alive Service**: Turn the service on/off
- **Ping Interval**: How often to ping (60-3600 seconds)
  - **60-300 seconds**: Very active (good for strict platforms)
  - **300-600 seconds**: Balanced (recommended)
  - **600-3600 seconds**: Conservative (may not work on all platforms)

## Status Monitoring

The dashboard shows real-time keep-alive statistics:

- **Total Pings**: Number of successful pings sent
- **Errors**: Number of failed ping attempts
- **Interval**: Current ping frequency
- **Last Ping**: Timestamp of the most recent successful ping

## Supported Hosting Platforms

This component works with any hosting platform that:
- Sleeps applications after inactivity
- Allows HTTP requests to wake up the application
- Supports background threads

### Tested Platforms

- ✅ **Render**: Works perfectly (sleeps after 15 minutes)
- ✅ **Heroku**: Works with free/hobby dynos (sleeps after 30 minutes)
- ✅ **Railway**: Works with free tier (sleeps after inactivity)
- ✅ **Fly.io**: Works with free tier
- ✅ **Koyeb**: Works with free tier

## Technical Details

### Implementation

- **Language**: Python 3.x
- **Threading**: Uses `threading.Thread` with daemon mode
- **HTTP Client**: Uses `requests.Session` for connection reuse
- **Error Handling**: Exponential backoff with configurable retries
- **Logging**: Integrated with the application's logging system

### Resource Usage

- **Memory**: Minimal (~1-2 MB)
- **CPU**: Negligible (only during ping requests)
- **Network**: ~1-2 KB per ping request
- **Bandwidth**: ~10-50 KB per hour (depending on interval)

### Security

- **Local Requests**: Only pings localhost (no external traffic)
- **No Data Exposure**: Only accesses the public web interface
- **User-Agent**: Identifies itself as "Vinted-Notifications-KeepAlive"

## Troubleshooting

### Service Not Starting

1. Check that the web UI is running on the configured port
2. Verify the keep-alive service is enabled in configuration
3. Check application logs for error messages

### High Error Count

1. Verify the web UI port is correct
2. Check if the application is experiencing issues
3. Consider increasing the ping interval
4. Review application logs for connection errors

### Platform Still Sleeping

1. Decrease the ping interval (try 120-180 seconds)
2. Check platform-specific sleep timeouts
3. Verify the platform supports HTTP-based wake-up
4. Consider using platform-specific keep-alive solutions

## Environment Variables

No additional environment variables are required. The component uses the existing web UI configuration.

## Manual Control

You can also control the keep-alive service programmatically:

```python
import keep_alive

# Start with custom settings
keep_alive.start_keep_alive(
    ping_interval=180,  # 3 minutes
    timeout=30,         # 30 second timeout
    max_retries=3       # 3 retry attempts
)

# Check status
status = keep_alive.get_keep_alive_status()
print(f"Ping count: {status['ping_count']}")

# Stop service
keep_alive.stop_keep_alive()
```

## Best Practices

1. **Start Conservative**: Begin with a 5-minute interval and adjust as needed
2. **Monitor Errors**: Keep an eye on the error count in the dashboard
3. **Platform Research**: Check your hosting platform's specific sleep policies
4. **Resource Awareness**: Consider your bandwidth limits on free tiers
5. **Backup Plans**: Have alternative hosting options if keep-alive doesn't work

## Limitations

- Only works if the web UI is accessible
- Requires the application to be running to start the service
- May not work on platforms with very aggressive sleep policies
- Uses additional bandwidth (minimal but worth considering on limited plans)

## Support

If you encounter issues:

1. Check the application logs for error messages
2. Verify your hosting platform's sleep policies
3. Test with different ping intervals
4. Consider platform-specific alternatives if needed