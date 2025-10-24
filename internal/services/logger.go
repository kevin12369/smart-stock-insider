package services

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"
)

type Logger struct {
	infoLogger    *log.Logger
	errorLogger   *log.Logger
	debugLogger   *log.Logger
	logFile       *os.File
	debugMode     bool
}

var AppLogger *Logger

// InitLogger 初始化日志系统
func InitLogger(debugMode bool) error {
	// 创建logs目录
	logDir := "logs"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return fmt.Errorf("创建日志目录失败: %v", err)
	}

	// 创建日志文件
	timestamp := time.Now().Format("2006-01-02")
	logFileName := filepath.Join(logDir, fmt.Sprintf("smart-stock-%s.log", timestamp))

	logFile, err := os.OpenFile(logFileName, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		return fmt.Errorf("打开日志文件失败: %v", err)
	}

	// 创建日志记录器
	infoLogger := log.New(logFile, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)
	errorLogger := log.New(logFile, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)
	debugLogger := log.New(os.Stdout, "DEBUG: ", log.Ldate|log.Ltime|log.Lshortfile)

	AppLogger = &Logger{
		infoLogger:  infoLogger,
		errorLogger: errorLogger,
		debugLogger: debugLogger,
		logFile:     logFile,
		debugMode:   debugMode,
	}

	AppLogger.Info("日志系统初始化完成")
	return nil
}

// Info 记录信息日志
func (l *Logger) Info(format string, v ...interface{}) {
	message := fmt.Sprintf(format, v...)
	l.infoLogger.Println(message)
	if l.debugMode {
		fmt.Printf("[INFO] %s\n", message)
	}
}

// Error 记录错误日志
func (l *Logger) Error(format string, v ...interface{}) {
	message := fmt.Sprintf(format, v...)
	l.errorLogger.Println(message)
	if l.debugMode {
		fmt.Printf("[ERROR] %s\n", message)
	}
}

// Debug 记录调试日志
func (l *Logger) Debug(format string, v ...interface{}) {
	message := fmt.Sprintf(format, v...)
	if l.debugMode {
		l.debugLogger.Println(message)
	}
}

// Close 关闭日志文件
func (l *Logger) Close() error {
	if l.logFile != nil {
		l.Info("日志系统关闭")
		return l.logFile.Close()
	}
	return nil
}

// LogStartup 记录应用启动信息
func (l *Logger) LogStartup(appName, version string) {
	l.Info("=== 应用启动 ===")
	l.Info("应用名称: %s", appName)
	l.Info("版本: %s", version)
	l.Info("启动时间: %s", time.Now().Format("2006-01-02 15:04:05"))
}

// LogShutdown 记录应用关闭信息
func (l *Logger) LogShutdown() {
	l.Info("=== 应用关闭 ===")
	l.Info("关闭时间: %s", time.Now().Format("2006-01-02 15:04:05"))
}