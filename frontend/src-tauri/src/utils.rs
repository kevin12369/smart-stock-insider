use std::fs;
use std::path::Path;
use log::{info, error};

/// Utility functions for the application

/// Create directory if it doesn't exist
pub fn ensure_dir_exists(path: &Path) -> Result<(), std::io::Error> {
    if !path.exists() {
        fs::create_dir_all(path)?;
        info!("Created directory: {:?}", path);
    }
    Ok(())
}

/// Write content to file
pub fn write_to_file(path: &Path, content: &str) -> Result<(), std::io::Error> {
    ensure_dir_exists(path.parent().unwrap())?;
    fs::write(path, content)?;
    info!("Wrote content to file: {:?}", path);
    Ok(())
}

/// Read content from file
pub fn read_from_file(path: &Path) -> Result<String, std::io::Error> {
    if path.exists() {
        let content = fs::read_to_string(path)?;
        info!("Read content from file: {:?}", path);
        Ok(content)
    } else {
        error!("File not found: {:?}", path);
        Err(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            format!("File not found: {:?}", path),
        ))
    }
}

/// Get application data directory
pub fn get_app_data_dir() -> Option<PathBuf> {
    let app_data = dirs::data_dir()?.join("smart-stock-insider");
    Some(app_data)
}

/// Get application logs directory
pub fn get_app_logs_dir() -> Option<PathBuf> {
    get_app_data_dir().map(|mut path| {
        path.push("logs");
        path
    })
}

/// Format file size to human readable string
pub fn format_file_size(bytes: u64) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB", "TB"];
    let mut size = bytes as f64;
    let mut unit_index = 0;

    while size >= 1024.0 && unit_index < UNITS.len() - 1 {
        size /= 1024.0;
        unit_index += 1;
    }

    if unit_index == 0 {
        format!("{} {}", bytes, UNITS[unit_index])
    } else {
        format!("{:.2} {}", size, UNITS[unit_index])
    }
}

/// Validate URL format
pub fn is_valid_url(url: &str) -> bool {
    url.starts_with("http://") || url.starts_with("https://")
}

/// Get current timestamp as string
pub fn get_timestamp() -> String {
    use chrono::Utc;
    Utc::now().format("%Y-%m-%d %H:%M:%S UTC").to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_file_size() {
        assert_eq!(format_file_size(512), "512 B");
        assert_eq!(format_file_size(1024), "1.00 KB");
        assert_eq!(format_file_size(1536), "1.50 KB");
        assert_eq!(format_file_size(1048576), "1.00 MB");
    }

    #[test]
    fn test_is_valid_url() {
        assert!(is_valid_url("https://example.com"));
        assert!(is_valid_url("http://localhost:8000"));
        assert!(!is_valid_url("ftp://example.com"));
        assert!(!is_valid_url("example.com"));
    }
}