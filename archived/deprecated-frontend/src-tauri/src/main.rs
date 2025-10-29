// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::env;
use log::{info, LevelFilter};
use env_logger::Builder;

mod commands;
mod utils;

use commands::*;

fn main() {
    // Initialize logger
    init_logger();

    info!("Starting 智股通 (Smart Stock Insider) application...");

    // Initialize dotenv for environment variables
    dotenv::dotenv().ok();

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_window::init())
        .invoke_handler(tauri::generate_handler![
            get_app_info,
            open_external_url,
            show_in_folder,
            get_system_info,
            check_for_updates,
            restart_app,
            minimize_to_tray,
            show_notification
        ])
        .setup(|app| {
            info!("Application setup completed successfully");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

/// Initialize the logger with appropriate configuration
fn init_logger() {
    Builder::new()
        .filter_level(LevelFilter::Info)
        .filter_module("tauri", LevelFilter::Warn)
        .init();
}