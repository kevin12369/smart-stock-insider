package utils

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"
)

// LogLevel 日志级别
type LogLevel int

const (
	DebugLevel LogLevel = iota
	InfoLevel
	WarnLevel
	ErrorLevel
	FatalLevel
)

var logLevelNames = map[LogLevel]string{
	DebugLevel: "DEBUG",
	InfoLevel:  "INFO",
	WarnLevel:  "WARN",
	ErrorLevel: "ERROR",
	FatalLevel: "FATAL",
}

// Logger 日志记录器接口
type Logger interface {
	Debug(msg string, args ...interface{})
	Info(msg string, args ...interface{})
	Warn(msg string, args ...interface{})
	Error(msg string, args ...interface{})
	Fatal(msg string, args ...interface{})
	Debugf(format string, args ...interface{})
	Infof(format string, args ...interface{})
	Warnf(format string, args ...interface{})
	Errorf(format string, args ...interface{})
	Fatalf(format string, args ...interface{})
	SetLevel(level LogLevel)
	GetLevel() LogLevel
	SetOutput(w io.Writer)
	AddHook(hook Hook)
}

// Hook 日志钩子函数
type Hook func(level LogLevel, message string, fields map[string]interface{})

// LogEntry 日志条目
type LogEntry struct {
	Level     LogLevel                 `json:"level"`
	Message   string                   `json:"message"`
	Timestamp time.Time                `json:"timestamp"`
	Caller    string                   `json:"caller"`
	File      string                   `json:"file"`
	Line      int                      `json:"line"`
	Fields    map[string]interface{}    `json:"fields,omitempty"`
	RequestID string                   `json:"request_id,omitempty"`
	UserID    string                   `json:"user_id,omitempty"`
	TraceID   string                   `json:"trace_id,omitempty"`
}

// StandardLogger 标准日志记录器
type StandardLogger struct {
	level    LogLevel
	output   io.Writer
	mu       sync.RWMutex
	hooks    []Hook
	fields   map[string]interface{}
}

// NewStandardLogger 创建标准日志记录器
func NewStandardLogger() *StandardLogger {
	return &StandardLogger{
		level:  InfoLevel,
		output: os.Stdout,
		hooks:  make([]Hook, 0),
		fields: make(map[string]interface{}),
	}
}

// NewFileLogger 创建文件日志记录器
func NewFileLogger(filename string, level LogLevel) (*StandardLogger, error) {
	// 确保目录存在
	dir := filepath.Dir(filename)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, fmt.Errorf("创建日志目录失败: %v", err)
	}

	// 创建或打开日志文件
	file, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return nil, fmt.Errorf("打开日志文件失败: %v", err)
	}

	logger := NewStandardLogger()
	logger.SetOutput(file)
	logger.SetLevel(level)

	return logger, nil
}

// NewMultiLogger 创建多重输出日志记录器
func NewMultiLogger(outputs ...io.Writer) *StandardLogger {
	var writers []io.Writer
	for _, w := range outputs {
		writers = append(writers, w)
	}

	multiWriter := io.MultiWriter(writers...)
	logger := NewStandardLogger()
	logger.SetOutput(multiWriter)

	return logger
}

// SetLevel 设置日志级别
func (l *StandardLogger) SetLevel(level LogLevel) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.level = level
}

// GetLevel 获取日志级别
func (l *StandardLogger) GetLevel() LogLevel {
	l.mu.RLock()
	defer l.mu.RUnlock()
	return l.level
}

// SetOutput 设置输出
func (l *StandardLogger) SetOutput(w io.Writer) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.output = w
}

// AddHook 添加钩子
func (l *StandardLogger) AddHook(hook Hook) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.hooks = append(l.hooks, hook)
}

// WithField 添加字段
func (l *StandardLogger) WithField(key string, value interface{}) *StandardLogger {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.fields[key] = value
	return l
}

// WithFields 添加多个字段
func (l *StandardLogger) WithFields(fields map[string]interface{}) *StandardLogger {
	l.mu.Lock()
	defer l.mu.Unlock()
	for k, v := range fields {
		l.fields[k] = v
	}
	return l
}

// Debug 记录调试日志
func (l *StandardLogger) Debug(msg string, args ...interface{}) {
	l.log(DebugLevel, msg, args...)
}

// Info 记录信息日志
func (l *StandardLogger) Info(msg string, args ...interface{}) {
	l.log(InfoLevel, msg, args...)
}

// Warn 记录警告日志
func (l *StandardLogger) Warn(msg string, args ...interface{}) {
	l.log(WarnLevel, msg, args...)
}

// Error 记录错误日志
func (l *StandardLogger) Error(msg string, args ...interface{}) {
	l.log(ErrorLevel, msg, args...)
}

// Fatal 记录致命错误日志
func (l *StandardLogger) Fatal(msg string, args ...interface{}) {
	l.log(FatalLevel, msg, args...)
	os.Exit(1)
}

// Debugf 格式化记录调试日志
func (l *StandardLogger) Debugf(format string, args ...interface{}) {
	l.logf(DebugLevel, format, args...)
}

// Infof 格式化记录信息日志
func (l *StandardLogger) Infof(format string, args ...interface{}) {
	l.logf(InfoLevel, format, args...)
}

// Warnf 格式化记录警告日志
func (l *StandardLogger) Warnf(format string, args ...interface{}) {
	l.logf(WarnLevel, format, args...)
}

// Errorf 格式化记录错误日志
func (l *StandardLogger) Errorf(format string, args ...interface{}) {
	l.logf(ErrorLevel, format, args...)
}

// Fatalf 格式化记录致命错误日志
func (l *StandardLogger) Fatalf(format string, args ...interface{}) {
	l.logf(FatalLevel, format, args...)
	os.Exit(1)
}

// log 内部日志记录方法
func (l *StandardLogger) log(level LogLevel, msg string, args ...interface{}) {
	if !l.shouldLog(level) {
		return
	}

	// 格式化消息
	formattedMsg := msg
	if len(args) > 0 {
		formattedMsg = fmt.Sprintf(msg, args...)
	}

	// 创建日志条目
	entry := l.createLogEntry(level, formattedMsg)

	// 调用钩子
	l.callHooks(entry)

	// 输出日志
	l.writeEntry(entry)
}

// logf 内部格式化日志记录方法
func (l *StandardLogger) logf(level LogLevel, format string, args ...interface{}) {
	if !l.shouldLog(level) {
		return
	}

	// 格式化消息
	formattedMsg := fmt.Sprintf(format, args...)

	// 创建日志条目
	entry := l.createLogEntry(level, formattedMsg)

	// 调用钩子
	l.callHooks(entry)

	// 输出日志
	l.writeEntry(entry)
}

// shouldLog 检查是否应该记录该级别的日志
func (l *StandardLogger) shouldLog(level LogLevel) bool {
	l.mu.RLock()
	defer l.mu.RUnlock()
	return level >= l.level
}

// createLogEntry 创建日志条目
func (l *StandardLogger) createLogEntry(level LogLevel, msg string) *LogEntry {
	entry := &LogEntry{
		Level:     level,
		Message:   msg,
		Timestamp: time.Now(),
		Fields:    make(map[string]interface{}),
	}

	// 复制全局字段
	for k, v := range l.fields {
		entry.Fields[k] = v
	}

	// 获取调用者信息
	if pc, file, line, ok := runtime.Caller(2); ok {
		entry.Caller = runtime.FuncForPC(pc).Name()
		entry.File = filepath.Base(file)
		entry.Line = line
	}

	return entry
}

// callHooks 调用所有钩子
func (l *StandardLogger) callHooks(entry *LogEntry) {
	l.mu.RLock()
	hooks := make([]Hook, len(l.hooks))
	copy(hooks, l.hooks)
	l.mu.RUnlock()

	for _, hook := range hooks {
		hook(entry.Level, entry.Message, entry.Fields)
	}
}

// writeEntry 输出日志条目
func (l *StandardLogger) writeEntry(entry *LogEntry) {
	l.mu.RLock()
	output := l.output
	l.mu.RUnlock()

	if output == nil {
		return
	}

	// 格式化日志行
	logLine := l.formatEntry(entry)

	// 写入输出
	fmt.Fprintln(output, logLine)
}

// formatEntry 格式化日志条目
func (l *StandardLogger) formatEntry(entry *LogEntry) string {
	// 基础格式: 时间戳 [级别] 文件:行号 消息
	timestamp := entry.Timestamp.Format("2006-01-02 15:04:05.000")
	levelName := logLevelNames[entry.Level]

	var parts []string
	parts = append(parts, timestamp)
	parts = append(parts, fmt.Sprintf("[%s]", levelName))

	if entry.File != "" && entry.Line > 0 {
		parts = append(parts, fmt.Sprintf("%s:%d", entry.File, entry.Line))
	}

	parts = append(parts, entry.Message)

	// 添加字段信息
	if len(entry.Fields) > 0 {
		fieldsStr := l.formatFields(entry.Fields)
		parts = append(parts, fieldsStr)
	}

	return strings.Join(parts, " ")
}

// Write 实现io.Writer接口
func (l *StandardLogger) Write(p []byte) (n int, err error) {
	l.mu.RLock()
	output := l.output
	l.mu.RUnlock()

	if output == nil {
		return 0, fmt.Errorf("output is nil")
	}

	return output.Write(p)
}

// formatFields 格式化字段
func (l *StandardLogger) formatFields(fields map[string]interface{}) string {
	if len(fields) == 0 {
		return ""
	}

	var parts []string
	for k, v := range fields {
		parts = append(parts, fmt.Sprintf("%s=%v", k, v))
	}

	return fmt.Sprintf("[%s]", strings.Join(parts, ", "))
}

// LoggerAdapter 日志适配器，适配现有的Logger接口
type LoggerAdapter struct {
	logger Logger
}

// NewLoggerAdapter 创建日志适配器
func NewLoggerAdapter(logger Logger) *LoggerAdapter {
	return &LoggerAdapter{logger: logger}
}

func (la *LoggerAdapter) Debug(msg string, args ...interface{}) {
	la.logger.Debug(msg, args...)
}

func (la *LoggerAdapter) Info(msg string, args ...interface{}) {
	la.logger.Info(msg, args...)
}

func (la *LoggerAdapter) Warn(msg string, args ...interface{}) {
	la.logger.Warn(msg, args...)
}

func (la *LoggerAdapter) Error(msg string, args ...interface{}) {
	la.logger.Error(msg, args...)
}

func (la *LoggerAdapter) Fatal(msg string, args ...interface{}) {
	la.logger.Fatal(msg, args...)
}

func (la *LoggerAdapter) Debugf(format string, args ...interface{}) {
	la.logger.Debugf(format, args...)
}

func (la *LoggerAdapter) Infof(format string, args ...interface{}) {
	la.logger.Infof(format, args...)
}

func (la *LoggerAdapter) Warnf(format string, args ...interface{}) {
	la.logger.Warnf(format, args...)
}

func (la *LoggerAdapter) Errorf(format string, args ...interface{}) {
	la.logger.Errorf(format, args...)
}

func (la *LoggerAdapter) Fatalf(format string, args ...interface{}) {
	la.logger.Fatalf(format, args...)
}

func (la *LoggerAdapter) AddHook(hook Hook) {
	// 如果底层logger支持AddHook，则转发
	if loggerWithHook, ok := la.logger.(interface{ AddHook(Hook) }); ok {
		loggerWithHook.AddHook(hook)
	}
}

func (la *LoggerAdapter) SetLevel(level LogLevel) {
	// 如果底层logger支持SetLevel，则转发
	if loggerWithLevel, ok := la.logger.(interface{ SetLevel(LogLevel) }); ok {
		loggerWithLevel.SetLevel(level)
	}
}

func (la *LoggerAdapter) GetLevel() LogLevel {
	// 如果底层logger支持GetLevel，则转发
	if loggerWithLevel, ok := la.logger.(interface{ GetLevel() LogLevel }); ok {
		return loggerWithLevel.GetLevel()
	}
	return InfoLevel // 默认级别
}

func (la *LoggerAdapter) SetOutput(w io.Writer) {
	// 如果底层logger支持SetOutput，则转发
	if loggerWithOutput, ok := la.logger.(interface{ SetOutput(io.Writer) }); ok {
		loggerWithOutput.SetOutput(w)
	}
}

// ContextLogger 上下文日志记录器
type ContextLogger struct {
	logger Logger
	fields map[string]interface{}
}

// NewContextLogger 创建上下文日志记录器
func NewContextLogger(logger Logger) *ContextLogger {
	return &ContextLogger{
		logger: logger,
		fields: make(map[string]interface{}),
	}
}

// WithField 添加字段
func (cl *ContextLogger) WithField(key string, value interface{}) *ContextLogger {
	cl.fields[key] = value
	return cl
}

// WithFields 添加多个字段
func (cl *ContextLogger) WithFields(fields map[string]interface{}) *ContextLogger {
	for k, v := range fields {
		cl.fields[k] = v
	}
	return cl
}

// WithRequestID 添加请求ID
func (cl *ContextLogger) WithRequestID(requestID string) *ContextLogger {
	return cl.WithField("request_id", requestID)
}

// WithUserID 添加用户ID
func (cl *ContextLogger) WithUserID(userID string) *ContextLogger {
	return cl.WithField("user_id", userID)
}

// WithTraceID 添加跟踪ID
func (cl *ContextLogger) WithTraceID(traceID string) *ContextLogger {
	return cl.WithField("trace_id", traceID)
}

// WithError 添加错误信息
func (cl *ContextLogger) WithError(err error) *ContextLogger {
	if err != nil {
		cl.WithField("error", err.Error())
		if appErr, ok := err.(*AppError); ok {
			cl.WithField("error_type", appErr.Type)
			cl.WithField("error_code", appErr.Code)
			if appErr.Context != nil {
				cl.WithFields(appErr.Context)
			}
		}
	}
	return cl
}

// Debug 记录调试日志
func (cl *ContextLogger) Debug(msg string, args ...interface{}) {
	cl.logWithFields(cl.logger.Debug, msg, args...)
}

// Info 记录信息日志
func (cl *ContextLogger) Info(msg string, args ...interface{}) {
	cl.logWithFields(cl.logger.Info, msg, args...)
}

// Warn 记录警告日志
func (cl *ContextLogger) Warn(msg string, args ...interface{}) {
	cl.logWithFields(cl.logger.Warn, msg, args...)
}

// Error 记录错误日志
func (cl *ContextLogger) Error(msg string, args ...interface{}) {
	cl.logWithFields(cl.logger.Error, msg, args...)
}

// Fatal 记录致命错误日志
func (cl *ContextLogger) Fatal(msg string, args ...interface{}) {
	cl.logWithFields(cl.logger.Fatal, msg, args...)
}

// Debugf 格式化记录调试日志
func (cl *ContextLogger) Debugf(format string, args ...interface{}) {
	cl.logWithFieldsf(cl.logger.Debugf, format, args...)
}

// Infof 格式化记录信息日志
func (cl *ContextLogger) Infof(format string, args ...interface{}) {
	cl.logWithFieldsf(cl.logger.Infof, format, args...)
}

// Warnf 格式化记录警告日志
func (cl *ContextLogger) Warnf(format string, args ...interface{}) {
	cl.logWithFieldsf(cl.logger.Warnf, format, args...)
}

// Errorf 格式化记录错误日志
func (cl *ContextLogger) Errorf(format string, args ...interface{}) {
	cl.logWithFieldsf(cl.logger.Errorf, format, args...)
}

// Fatalf 格式化记录致命错误日志
func (cl *ContextLogger) Fatalf(format string, args ...interface{}) {
	cl.logWithFieldsf(cl.logger.Fatalf, format, args...)
}

// logWithFields 带字段记录日志
func (cl *ContextLogger) logWithFields(logFunc func(string, ...interface{}), msg string, args ...interface{}) {
	// 创建临时logger来包含字段
	tempLogger := NewStandardLogger()
	tempLogger.SetLevel(cl.logger.GetLevel())

	// 复制钩子（如果标准logger支持）
	if stdLogger, ok := cl.logger.(*StandardLogger); ok {
		stdLogger.mu.RLock()
		hooks := make([]Hook, len(stdLogger.hooks))
		copy(hooks, stdLogger.hooks)
		stdLogger.mu.RUnlock()

		for _, hook := range hooks {
			tempLogger.AddHook(hook)
		}
	}

	// 添加字段
	tempLogger.WithFields(cl.fields)

	// 记录日志
	logFunc(msg, args...)
}

// logWithFieldsf 带字段格式化记录日志
func (cl *ContextLogger) logWithFieldsf(logFunc func(string, ...interface{}), format string, args ...interface{}) {
	// 创建临时logger来包含字段
	tempLogger := NewStandardLogger()
	tempLogger.SetLevel(cl.logger.GetLevel())

	// 复制钩子（如果标准logger支持）
	if stdLogger, ok := cl.logger.(*StandardLogger); ok {
		stdLogger.mu.RLock()
		hooks := make([]Hook, len(stdLogger.hooks))
		copy(hooks, stdLogger.hooks)
		stdLogger.mu.RUnlock()

		for _, hook := range hooks {
			tempLogger.AddHook(hook)
		}
	}

	// 添加字段
	tempLogger.WithFields(cl.fields)

	// 记录日志
	logFunc(format, args...)
}

// 全局日志记录器
var (
	GlobalLogger Logger
)

// InitLogger 初始化全局日志记录器
func InitLogger() error {
	// 创建日志目录
	logDir := "logs"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return fmt.Errorf("创建日志目录失败: %v", err)
	}

	// 创建控制台日志记录器
	consoleLogger := NewStandardLogger()
	consoleLogger.SetLevel(InfoLevel)

	// 创建文件日志记录器
	fileLogger, err := NewFileLogger(filepath.Join(logDir, "app.log"), DebugLevel)
	if err != nil {
		return fmt.Errorf("创建文件日志记录器失败: %v", err)
	}

	// 创建错误日志记录器
	errorLogger, err := NewFileLogger(filepath.Join(logDir, "error.log"), ErrorLevel)
	if err != nil {
		return fmt.Errorf("创建错误日志记录器失败: %v", err)
	}

	// 创建多重输出日志记录器 - 通过io.MultiWriter
	multiWriter := io.MultiWriter(consoleLogger, fileLogger, errorLogger)
	multiLogger := NewStandardLogger()
	multiLogger.SetOutput(multiWriter)
	multiLogger.SetLevel(DebugLevel)

	// 设置全局日志记录器
	GlobalLogger = NewLoggerAdapter(multiLogger)

	// 添加错误钩子
	multiLogger.AddHook(func(level LogLevel, message string, fields map[string]interface{}) {
		if level >= ErrorLevel {
			// 这里可以添加错误通知逻辑
			// 例如：发送邮件、Slack通知等
		}
	})

	return nil
}

// GetGlobalLogger 获取全局日志记录器
func GetGlobalLogger() Logger {
	if GlobalLogger == nil {
		// 如果没有初始化，创建一个默认的
		GlobalLogger = NewLoggerAdapter(NewStandardLogger())
	}
	return GlobalLogger
}

// Debug 全局调试日志
func Debug(msg string, args ...interface{}) {
	GetGlobalLogger().Debug(msg, args...)
}

// Info 全局信息日志
func Info(msg string, args ...interface{}) {
	GetGlobalLogger().Info(msg, args...)
}

// Warn 全局警告日志
func Warn(msg string, args ...interface{}) {
	GetGlobalLogger().Warn(msg, args...)
}

// Error 全局错误日志
func Error(msg string, args ...interface{}) {
	GetGlobalLogger().Error(msg, args...)
}

// Fatal 全局致命错误日志
func Fatal(msg string, args ...interface{}) {
	GetGlobalLogger().Fatal(msg, args...)
}

// Debugf 全局格式化调试日志
func Debugf(format string, args ...interface{}) {
	GetGlobalLogger().Debugf(format, args...)
}

// Infof 全局格式化信息日志
func Infof(format string, args ...interface{}) {
	GetGlobalLogger().Infof(format, args...)
}

// Warnf 全局格式化警告日志
func Warnf(format string, args ...interface{}) {
	GetGlobalLogger().Warnf(format, args...)
}

// Errorf 全局格式化错误日志
func Errorf(format string, args ...interface{}) {
	GetGlobalLogger().Errorf(format, args...)
}

// Fatalf 全局格式化致命错误日志
func Fatalf(format string, args ...interface{}) {
	GetGlobalLogger().Fatalf(format, args...)
}