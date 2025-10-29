use serde::{Deserialize, Serialize};
use tauri::{Manager, Window};
use std::process::Command;
use log::info;

#[derive(Debug, Serialize, Deserialize)]
pub struct AppInfo {
    name: String,
    version: String,
    description: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemInfo {
    os: String,
    arch: String,
    memory: String,
}

/// Get application information
#[tauri::command]
pub fn get_app_info() -> Result<AppInfo, String> {
    Ok(AppInfo {
        name: "智股通".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        description: "基于AI的桌面投资研究平台".to_string(),
    })
}

/// Open external URL in default browser
#[tauri::command]
pub fn open_external_url(url: String) -> Result<(), String> {
    info!("Opening external URL: {}", url);

    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args(["/C", "start", &url])
            .spawn()
            .map_err(|e| format!("Failed to open URL: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(&url)
            .spawn()
            .map_err(|e| format!("Failed to open URL: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(&url)
            .spawn()
            .map_err(|e| format!("Failed to open URL: {}", e))?;
    }

    Ok(())
}

/// Show file in folder
#[tauri::command]
pub fn show_in_folder(path: String) -> Result<(), String> {
    info!("Showing file in folder: {}", path);

    #[cfg(target_os = "windows")]
    {
        Command::new("explorer")
            .args(["/select,", &path])
            .spawn()
            .map_err(|e| format!("Failed to show in folder: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .args(["-R", &path])
            .spawn()
            .map_err(|e| format!("Failed to show in folder: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        // For Linux, we can try different file managers
        let managers = ["nautilus", "dolphin", "thunar", "pcmanfm"];
        for manager in managers {
            if Command::new(manager)
                .arg(&path)
                .spawn()
                .is_ok()
            {
                return Ok(());
            }
        }
        return Err("No suitable file manager found".to_string());
    }

    Ok(())
}

/// Get system information
#[tauri::command]
pub fn get_system_info() -> Result<SystemInfo, String> {
    Ok(SystemInfo {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        memory: "Unknown".to_string(), // TODO: Implement memory detection
    })
}

/// Check for application updates
#[tauri::command]
pub async fn check_for_updates() -> Result<bool, String> {
    info!("Checking for application updates...");
    // TODO: Implement update checking logic
    Ok(false) // No updates available for now
}

/// Restart the application
#[tauri::command]
pub fn restart_app(app: tauri::AppHandle) -> Result<(), String> {
    info!("Restarting application...");
    app.restart();
    Ok(())
}

/// Minimize window to system tray
#[tauri::command]
pub fn minimize_to_tray(window: Window) -> Result<(), String> {
    info!("Minimizing window to system tray");
    window.minimize().map_err(|e| format!("Failed to minimize window: {}", e))?;
    Ok(())
}

/// Show system notification
#[tauri::command]
pub fn show_notification(title: String, body: String) -> Result<(), String> {
    info!("Showing notification: {} - {}", title, body);
    // TODO: Implement notification system
    Ok(())
}