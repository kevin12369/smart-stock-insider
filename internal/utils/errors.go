package utils

import (
	"fmt"
	"math"
	"runtime"
	"strings"
	"time"
)

// ErrorType 错误类型
type ErrorType string

const (
	ErrorTypeValidation    ErrorType = "validation"
	ErrorTypeDatabase     ErrorType = "database"
	ErrorTypeAPI          ErrorType = "api"
	ErrorTypeBusiness     ErrorType = "business"
	ErrorTypeSystem       ErrorType = "system"
	ErrorTypeNetwork      ErrorType = "network"
	ErrorTypeTimeout      ErrorType = "timeout"
	ErrorTypeAuth         ErrorType = "auth"
	ErrorTypePermission   ErrorType = "permission"
	ErrorTypeNotFound     ErrorType = "not_found"
	ErrorTypeConflict     ErrorType = "conflict"
	ErrorTypeRateLimit    ErrorType = "rate_limit"
	ErrorTypeDependency   ErrorType = "dependency"
)

// AppError 应用错误
type AppError struct {
	Type        ErrorType `json:"type"`
	Code        string    `json:"code"`
	Message     string    `json:"message"`
	Details     string    `json:"details,omitempty"`
	Cause       error     `json:"-"`
	Context     map[string]interface{} `json:"context,omitempty"`
	StackTrace  []string  `json:"stack_trace,omitempty"`
	Timestamp   string    `json:"timestamp"`
	RequestID   string    `json:"request_id,omitempty"`
	UserID      string    `json:"user_id,omitempty"`
	Severity    string    `json:"severity"`        // low, medium, high, critical
	Retryable   bool      `json:"retryable"`
}

// Error 实现error接口
func (e *AppError) Error() string {
	if e.Details != "" {
		return fmt.Sprintf("[%s] %s: %s - %s", e.Type, e.Code, e.Message, e.Details)
	}
	return fmt.Sprintf("[%s] %s: %s", e.Type, e.Code, e.Message)
}

// Unwrap 支持错误链
func (e *AppError) Unwrap() error {
	return e.Cause
}

// NewAppError 创建新的应用错误
func NewAppError(errorType ErrorType, code, message string) *AppError {
	return &AppError{
		Type:      errorType,
		Code:      code,
		Message:   message,
		Timestamp: getCurrentTimestamp(),
		Severity:  determineSeverity(errorType),
		Retryable: isRetryable(errorType),
	}
}

// WrapError 包装已有错误
func WrapError(err error, errorType ErrorType, code, message string) *AppError {
	if err == nil {
		return NewAppError(errorType, code, message)
	}

	appErr := &AppError{
		Type:      errorType,
		Code:      code,
		Message:   message,
		Cause:     err,
		Timestamp: getCurrentTimestamp(),
		Severity:  determineSeverity(errorType),
		Retryable: isRetryable(errorType),
	}

	// 如果被包装的错误也是AppError，保留一些信息
	if wrappedAppErr, ok := err.(*AppError); ok {
		appErr.Context = wrappedAppErr.Context
		appErr.RequestID = wrappedAppErr.RequestID
		appErr.UserID = wrappedAppErr.UserID
	}

	return appErr
}

// WithDetails 添加详细信息
func (e *AppError) WithDetails(details string) *AppError {
	e.Details = details
	return e
}

// WithContext 添加上下文信息
func (e *AppError) WithContext(key string, value interface{}) *AppError {
	if e.Context == nil {
		e.Context = make(map[string]interface{})
	}
	e.Context[key] = value
	return e
}

// WithRequestID 添加请求ID
func (e *AppError) WithRequestID(requestID string) *AppError {
	e.RequestID = requestID
	return e
}

// WithUserID 添加用户ID
func (e *AppError) WithUserID(userID string) *AppError {
	e.UserID = userID
	return e
}

// WithSeverity 设置严重程度
func (e *AppError) WithSeverity(severity string) *AppError {
	e.Severity = severity
	return e
}

// WithRetryable 设置是否可重试
func (e *AppError) WithRetryable(retryable bool) *AppError {
	e.Retryable = retryable
	return e
}

// WithStackTrace 添加堆栈跟踪
func (e *AppError) WithStackTrace() *AppError {
	e.StackTrace = getStackTrace()
	return e
}

// GetHTTPStatusCode 获取对应的HTTP状态码
func (e *AppError) GetHTTPStatusCode() int {
	switch e.Type {
	case ErrorTypeValidation:
		return 400
	case ErrorTypeAuth:
		return 401
	case ErrorTypePermission:
		return 403
	case ErrorTypeNotFound:
		return 404
	case ErrorTypeConflict:
		return 409
	case ErrorTypeRateLimit:
		return 429
	case ErrorTypeTimeout:
		return 408
	case ErrorTypeDependency:
		return 502
	case ErrorTypeSystem:
		return 500
	case ErrorTypeNetwork, ErrorTypeDatabase, ErrorTypeAPI:
		return 500
	case ErrorTypeBusiness:
		return 422
	default:
		return 500
	}
}

// IsRetryable 判断错误是否可重试
func (e *AppError) IsRetryable() bool {
	return e.Retryable
}

// 预定义错误
var (
	ErrInvalidInput        = NewAppError(ErrorTypeValidation, "INVALID_INPUT", "输入参数无效")
	ErrMissingParameter    = NewAppError(ErrorTypeValidation, "MISSING_PARAMETER", "缺少必需参数")
	ErrInvalidFormat      = NewAppError(ErrorTypeValidation, "INVALID_FORMAT", "数据格式无效")
	ErrOutOfRange         = NewAppError(ErrorTypeValidation, "OUT_OF_RANGE", "参数超出范围")

	ErrDatabaseConnection  = NewAppError(ErrorTypeDatabase, "DB_CONNECTION", "数据库连接失败")
	ErrDatabaseQuery      = NewAppError(ErrorTypeDatabase, "DB_QUERY", "数据库查询失败")
	ErrDatabaseTransaction = NewAppError(ErrorTypeDatabase, "DB_TRANSACTION", "数据库事务失败")
	ErrRecordNotFound      = NewAppError(ErrorTypeDatabase, "RECORD_NOT_FOUND", "记录不存在")
	ErrDuplicateRecord    = NewAppError(ErrorTypeDatabase, "DUPLICATE_RECORD", "记录已存在")

	ErrAPIRequest          = NewAppError(ErrorTypeAPI, "API_REQUEST", "API请求失败")
	ErrAPIResponse         = NewAppError(ErrorTypeAPI, "API_RESPONSE", "API响应错误")
	ErrAPIRateLimit        = NewAppError(ErrorTypeAPI, "API_RATE_LIMIT", "API请求频率限制")
	ErrAPITimeout          = NewAppError(ErrorTypeAPI, "API_TIMEOUT", "API请求超时")

	ErrNetworkConnection    = NewAppError(ErrorTypeNetwork, "NETWORK_CONNECTION", "网络连接失败")
	ErrNetworkTimeout       = NewAppError(ErrorTypeNetwork, "NETWORK_TIMEOUT", "网络请求超时")

	ErrAuthentication      = NewAppError(ErrorTypeAuth, "AUTH_FAILED", "身份验证失败")
	ErrUnauthorized        = NewAppError(ErrorTypeAuth, "UNAUTHORIZED", "未授权访问")
	ErrTokenExpired       = NewAppError(ErrorTypeAuth, "TOKEN_EXPIRED", "访问令牌已过期")
	ErrInvalidToken       = NewAppError(ErrorTypeAuth, "INVALID_TOKEN", "访问令牌无效")

	ErrPermissionDenied    = NewAppError(ErrorTypePermission, "PERMISSION_DENIED", "权限不足")
	ErrResourceForbidden   = NewAppError(ErrorTypePermission, "RESOURCE_FORBIDDEN", "资源访问被禁止")

	ErrResourceNotFound     = NewAppError(ErrorTypeNotFound, "RESOURCE_NOT_FOUND", "资源不存在")
	ErrStockNotFound       = NewAppError(ErrorTypeNotFound, "STOCK_NOT_FOUND", "股票不存在")
	ErrUserNotFound        = NewAppError(ErrorTypeNotFound, "USER_NOT_FOUND", "用户不存在")

	ErrConflict            = NewAppError(ErrorTypeConflict, "CONFLICT", "资源冲突")
	ErrVersionConflict     = NewAppError(ErrorTypeConflict, "VERSION_CONFLICT", "版本冲突")

	ErrBusinessRule        = NewAppError(ErrorTypeBusiness, "BUSINESS_RULE", "业务规则违反")
	ErrInsufficientData    = NewAppError(ErrorTypeBusiness, "INSUFFICIENT_DATA", "数据不足")
	ErrInvalidState        = NewAppError(ErrorTypeBusiness, "INVALID_STATE", "状态无效")

	ErrSystemError         = NewAppError(ErrorTypeSystem, "SYSTEM_ERROR", "系统错误")
	ErrServiceUnavailable   = NewAppError(ErrorTypeSystem, "SERVICE_UNAVAILABLE", "服务不可用")
	ErrConfiguration       = NewAppError(ErrorTypeSystem, "CONFIGURATION", "配置错误")
	ErrInternalServer      = NewAppError(ErrorTypeSystem, "INTERNAL_SERVER", "内部服务器错误")

	ErrTimeout             = NewAppError(ErrorTypeTimeout, "TIMEOUT", "操作超时")
	ErrRequestTimeout      = NewAppError(ErrorTypeTimeout, "REQUEST_TIMEOUT", "请求超时")

	ErrDependencyFailure   = NewAppError(ErrorTypeDependency, "DEPENDENCY_FAILURE", "依赖服务失败")
	ErrDependencyUnavailable = NewAppError(ErrorTypeDependency, "DEPENDENCY_UNAVAILABLE", "依赖服务不可用")
)

// determineSeverity 确定错误严重程度
func determineSeverity(errorType ErrorType) string {
	switch errorType {
	case ErrorTypeValidation:
		return "low"
	case ErrorTypeNotFound:
		return "medium"
	case ErrorTypeBusiness, ErrorTypeConflict:
		return "medium"
	case ErrorTypeNetwork, ErrorTypeDatabase, ErrorTypeAPI, ErrorTypeTimeout:
		return "high"
	case ErrorTypeAuth, ErrorTypePermission, ErrorTypeSystem, ErrorTypeDependency:
		return "critical"
	default:
		return "medium"
	}
}

// isRetryable 判断错误类型是否可重试
func isRetryable(errorType ErrorType) bool {
	switch errorType {
	case ErrorTypeNetwork, ErrorTypeDatabase, ErrorTypeAPI, ErrorTypeTimeout, ErrorTypeDependency:
		return true
	case ErrorTypeValidation, ErrorTypeAuth, ErrorTypePermission, ErrorTypeNotFound, ErrorTypeConflict, ErrorTypeBusiness, ErrorTypeSystem:
		return false
	default:
		return false
	}
}

// getCurrentTimestamp 获取当前时间戳字符串
func getCurrentTimestamp() string {
	return time.Now().Format("2006-01-02 15:04:05.000")
}

// getStackTrace 获取堆栈跟踪
func getStackTrace() []string {
	var stack []string
	for i := 1; i < 10; i++ {
		_, file, line, ok := runtime.Caller(i)
		if !ok {
			break
		}
		// 简化文件路径，只保留包名和函数名
		parts := strings.Split(file, "/")
		if len(parts) > 2 {
			file = strings.Join(parts[len(parts)-2:], "/")
		}
		stack = append(stack, fmt.Sprintf("%s:%d", file, line))
	}
	return stack
}

// ErrorHandler 错误处理器接口
type ErrorHandler interface {
	HandleError(err error) error
	CanHandle(err error) bool
	GetPriority() int
}

// DefaultErrorHandler 默认错误处理器
type DefaultErrorHandler struct {
	priority int
}

func NewDefaultErrorHandler() *DefaultErrorHandler {
	return &DefaultErrorHandler{
		priority: 0,
	}
}

func (h *DefaultErrorHandler) HandleError(err error) error {
	// 默认处理：记录日志并返回原错误
	// 这里可以集成日志系统
	return err
}

func (h *DefaultErrorHandler) CanHandle(err error) bool {
	return true // 默认处理器可以处理所有错误
}

func (h *DefaultErrorHandler) GetPriority() int {
	return h.priority
}

// ErrorChain 错误链
type ErrorChain struct {
	errors []error
}

func NewErrorChain() *ErrorChain {
	return &ErrorChain{
		errors: make([]error, 0),
	}
}

func (ec *ErrorChain) Add(err error) *ErrorChain {
	if err != nil {
		ec.errors = append(ec.errors, err)
	}
	return ec
}

func (ec *ErrorChain) HasErrors() bool {
	return len(ec.errors) > 0
}

func (ec *ErrorChain) GetErrors() []error {
	return ec.errors
}

func (ec *ErrorChain) GetFirstError() error {
	if len(ec.errors) > 0 {
		return ec.errors[0]
	}
	return nil
}

func (ec *ErrorChain) GetLastError() error {
	if len(ec.errors) > 0 {
		return ec.errors[len(ec.errors)-1]
	}
	return nil
}

func (ec *ErrorChain) Error() string {
	if !ec.HasErrors() {
		return "no errors"
	}

	var messages []string
	for _, err := range ec.errors {
		messages = append(messages, err.Error())
	}
	return strings.Join(messages, "; ")
}

// ErrorRecovery 错误恢复接口
type ErrorRecovery interface {
	CanRecover(err error) bool
	Recover(err error) error
}

// RetryConfig 重试配置
type RetryConfig struct {
	MaxAttempts   int
	InitialDelay  time.Duration
	MaxDelay      time.Duration
	Multiplier    float64
	RetryableErrors []ErrorType
}

func NewRetryConfig() *RetryConfig {
	return &RetryConfig{
		MaxAttempts:   3,
		InitialDelay:  time.Second,
		MaxDelay:      30 * time.Second,
		Multiplier:    2.0,
		RetryableErrors: []ErrorType{
			ErrorTypeNetwork,
			ErrorTypeDatabase,
			ErrorTypeAPI,
			ErrorTypeTimeout,
			ErrorTypeDependency,
		},
	}
}

// CanRetry 判断错误是否可重试
func (rc *RetryConfig) CanRetry(err error) bool {
	if appErr, ok := err.(*AppError); ok {
		for _, retryableType := range rc.RetryableErrors {
			if appErr.Type == retryableType {
				return true
			}
		}
		return appErr.IsRetryable()
	}
	return false
}

// GetDelay 获取重试延迟时间
func (rc *RetryConfig) GetDelay(attempt int) time.Duration {
	delay := time.Duration(float64(rc.InitialDelay) * math.Pow(rc.Multiplier, float64(attempt-1)))
	if delay > rc.MaxDelay {
		delay = rc.MaxDelay
	}
	return delay
}

// SafeExecute 安全执行函数，自动处理panic
func SafeExecute(fn func() error) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = NewAppError(ErrorTypeSystem, "PANIC", fmt.Sprintf("系统panic: %v", r))
		}
	}()

	return fn()
}

// SafeExecuteWithRetry 带重试的安全执行
func SafeExecuteWithRetry(fn func() error, config *RetryConfig) error {
	var lastErr error

	for attempt := 1; attempt <= config.MaxAttempts; attempt++ {
		err := SafeExecute(fn)
		if err == nil {
			return nil
		}

		lastErr = err

		// 检查是否可重试
		if !config.CanRetry(err) {
			break
		}

		// 如果不是最后一次尝试，等待后重试
		if attempt < config.MaxAttempts {
			delay := config.GetDelay(attempt)
			time.Sleep(delay)
		}
	}

	return lastErr
}

// ErrorContext 错误上下文
type ErrorContext struct {
	RequestID   string                 `json:"request_id"`
	UserID      string                 `json:"user_id"`
	IPAddress   string                 `json:"ip_address"`
	UserAgent   string                 `json:"user_agent"`
	Method      string                 `json:"method"`
	Path        string                 `json:"path"`
	Headers     map[string]string      `json:"headers"`
	Params      map[string]interface{} `json:"params"`
	Timestamp   time.Time              `json:"timestamp"`
}

// NewErrorContext 创建错误上下文
func NewErrorContext() *ErrorContext {
	return &ErrorContext{
		Headers:   make(map[string]string),
		Params:    make(map[string]interface{}),
		Timestamp: time.Now(),
	}
}

// WithRequestID 添加请求ID
func (ec *ErrorContext) WithRequestID(requestID string) *ErrorContext {
	ec.RequestID = requestID
	return ec
}

// WithUserID 添加用户ID
func (ec *ErrorContext) WithUserID(userID string) *ErrorContext {
	ec.UserID = userID
	return ec
}

// WithIPAddress 添加IP地址
func (ec *ErrorContext) WithIPAddress(ip string) *ErrorContext {
	ec.IPAddress = ip
	return ec
}

// WithUserAgent 添加User-Agent
func (ec *ErrorContext) WithUserAgent(ua string) *ErrorContext {
	ec.UserAgent = ua
	return ec
}

// WithMethod 添加HTTP方法
func (ec *ErrorContext) WithMethod(method string) *ErrorContext {
	ec.Method = method
	return ec
}

// WithPath 添加请求路径
func (ec *ErrorContext) WithPath(path string) *ErrorContext {
	ec.Path = path
	return ec
}

// WithHeader 添加请求头
func (ec *ErrorContext) WithHeader(key, value string) *ErrorContext {
	if ec.Headers == nil {
		ec.Headers = make(map[string]string)
	}
	ec.Headers[key] = value
	return ec
}

// WithParam 添加请求参数
func (ec *ErrorContext) WithParam(key string, value interface{}) *ErrorContext {
	if ec.Params == nil {
		ec.Params = make(map[string]interface{})
	}
	ec.Params[key] = value
	return ec
}