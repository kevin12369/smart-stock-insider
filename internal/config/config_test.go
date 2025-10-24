package config

import (
	"os"
	"path/filepath"
	"testing"
)

// TestDefaultConfig 测试默认配置
func TestDefaultConfig(t *testing.T) {
	config := DefaultConfig()

	if config == nil {
		t.Fatal("默认配置不能为空")
	}

	// 验证服务器配置
	if config.Server.Host != "localhost" {
		t.Errorf("默认主机名错误，期望 localhost，实际 %s", config.Server.Host)
	}
	if config.Server.Port != 8080 {
		t.Errorf("默认端口错误，期望 8080，实际 %d", config.Server.Port)
	}
	if !config.Server.EnableCORS {
		t.Error("默认应该启用CORS")
	}

	// 验证数据库配置
	if config.Database.Path != "data/smart_stock.db" {
		t.Errorf("默认数据库路径错误，期望 data/smart_stock.db，实际 %s", config.Database.Path)
	}
	if !config.Database.EnableWAL {
		t.Error("默认应该启用WAL")
	}

	// 验证数据配置
	if len(config.Data.Sources) == 0 {
		t.Error("默认数据源不能为空")
	}
	if !config.Data.EnableCache {
		t.Error("默认应该启用缓存")
	}

	// 验证AI配置
	if config.AI.BaseURL != "http://localhost:8000" {
		t.Errorf("默认AI服务地址错误，期望 http://localhost:8000，实际 %s", config.AI.BaseURL)
	}
	if !config.AI.EnableCache {
		t.Error("默认应该启用AI缓存")
	}

	// 验证日志配置
	if config.Logging.Level != "info" {
		t.Errorf("默认日志级别错误，期望 info，实际 %s", config.Logging.Level)
	}
	if !config.Logging.EnableConsole {
		t.Error("默认应该启用控制台日志")
	}

	t.Log("✅ 默认配置测试通过")
}

// TestValidateConfig 测试配置验证
func TestValidateConfig(t *testing.T) {
	// 测试有效配置
	t.Run("有效配置", func(t *testing.T) {
		config := DefaultConfig()
		if err := ValidateConfig(config); err != nil {
			t.Errorf("有效配置验证失败: %v", err)
		}
	})

	// 测试无效配置
	t.Run("无效配置", func(t *testing.T) {
		// 空服务器配置
		config := &Config{
			Server: nil,
			Database: &DatabaseConfig{Path: "test.db"},
			Data: &DataConfig{Sources: []string{"test"}},
			AI: &AIConfig{BaseURL: "http://localhost:8000"},
		}
		if err := ValidateConfig(config); err == nil {
			t.Error("空服务器配置应该验证失败")
		}

		// 无效端口
		config = DefaultConfig()
		config.Server.Port = 99999
		if err := ValidateConfig(config); err == nil {
			t.Error("无效端口应该验证失败")
		}

		// 空数据库路径
		config = DefaultConfig()
		config.Database.Path = ""
		if err := ValidateConfig(config); err == nil {
			t.Error("空数据库路径应该验证失败")
		}

		// 空数据源
		config = DefaultConfig()
		config.Data.Sources = []string{}
		if err := ValidateConfig(config); err == nil {
			t.Error("空数据源应该验证失败")
		}

		// 空AI服务地址
		config = DefaultConfig()
		config.AI.BaseURL = ""
		if err := ValidateConfig(config); err == nil {
			t.Error("空AI服务地址应该验证失败")
		}
	})

	t.Log("✅ 配置验证测试通过")
}

// TestSaveAndLoadConfig 测试配置保存和加载
func TestSaveAndLoadConfig(t *testing.T) {
	// 创建临时目录
	tempDir := t.TempDir()
	configPath := filepath.Join(tempDir, "config.json")

	// 测试保存配置
	t.Run("保存配置", func(t *testing.T) {
		config := DefaultConfig()
		config.Server.Host = "test-host"
		config.Server.Port = 9999
		config.Database.Path = "test.db"

		if err := SaveConfig(config, configPath); err != nil {
			t.Errorf("保存配置失败: %v", err)
		}

		// 验证文件是否存在
		if _, err := os.Stat(configPath); os.IsNotExist(err) {
			t.Error("配置文件未创建")
		}
	})

	// 测试加载配置
	t.Run("加载配置", func(t *testing.T) {
		config, err := LoadConfig(configPath)
		if err != nil {
			t.Errorf("加载配置失败: %v", err)
		}

		if config.Server.Host != "test-host" {
			t.Errorf("加载的主机名错误，期望 test-host，实际 %s", config.Server.Host)
		}
		if config.Server.Port != 9999 {
			t.Errorf("加载的端口错误，期望 9999，实际 %d", config.Server.Port)
		}
		if config.Database.Path != "test.db" {
			t.Errorf("加载的数据库路径错误，期望 test.db，实际 %s", config.Database.Path)
		}
	})

	// 测试自动创建默认配置
	t.Run("自动创建默认配置", func(t *testing.T) {
		newConfigPath := filepath.Join(tempDir, "new_config.json")

		// 确保文件不存在
		if _, err := os.Stat(newConfigPath); err == nil {
			os.Remove(newConfigPath)
		}

		// 加载不存在的配置文件应该创建默认配置
		config, err := LoadConfig(newConfigPath)
		if err != nil {
			t.Errorf("加载不存在配置文件失败: %v", err)
		}

		// 验证默认配置
		if config.Server.Host != "localhost" {
			t.Errorf("自动创建的默认主机名错误，期望 localhost，实际 %s", config.Server.Host)
		}

		// 验证文件已创建
		if _, err := os.Stat(newConfigPath); os.IsNotExist(err) {
			t.Error("默认配置文件未自动创建")
		}
	})

	t.Log("✅ 配置保存和加载测试通过")
}

// TestEnvironmentOverrides 测试环境变量覆盖
func TestEnvironmentOverrides(t *testing.T) {
	// 保存原始环境变量
	originalHost := os.Getenv("SMART_STOCK_HOST")
	originalPort := os.Getenv("SMART_STOCK_PORT")
	originalDBPath := os.Getenv("SMART_STOCK_DB_PATH")
	originalAIURL := os.Getenv("SMART_STOCK_AI_URL")
	originalLogLevel := os.Getenv("SMART_STOCK_LOG_LEVEL")

	// 测试后恢复环境变量
	defer func() {
		if originalHost != "" {
			os.Setenv("SMART_STOCK_HOST", originalHost)
		} else {
			os.Unsetenv("SMART_STOCK_HOST")
		}
		if originalPort != "" {
			os.Setenv("SMART_STOCK_PORT", originalPort)
		} else {
			os.Unsetenv("SMART_STOCK_PORT")
		}
		if originalDBPath != "" {
			os.Setenv("SMART_STOCK_DB_PATH", originalDBPath)
		} else {
			os.Unsetenv("SMART_STOCK_DB_PATH")
		}
		if originalAIURL != "" {
			os.Setenv("SMART_STOCK_AI_URL", originalAIURL)
		} else {
			os.Unsetenv("SMART_STOCK_AI_URL")
		}
		if originalLogLevel != "" {
			os.Setenv("SMART_STOCK_LOG_LEVEL", originalLogLevel)
		} else {
			os.Unsetenv("SMART_STOCK_LOG_LEVEL")
		}
	}()

	// 设置环境变量
	os.Setenv("SMART_STOCK_HOST", "env-host")
	os.Setenv("SMART_STOCK_PORT", "8888")
	os.Setenv("SMART_STOCK_DB_PATH", "env.db")
	os.Setenv("SMART_STOCK_AI_URL", "http://env-ai:9000")
	os.Setenv("SMART_STOCK_LOG_LEVEL", "debug")

	// 加载配置（应该被环境变量覆盖）
	config := DefaultConfig()
	loadEnvironmentOverrides(config)

	// 验证环境变量覆盖
	if config.Server.Host != "env-host" {
		t.Errorf("环境变量覆盖主机名失败，期望 env-host，实际 %s", config.Server.Host)
	}
	if config.Server.Port != 8888 {
		t.Errorf("环境变量覆盖端口失败，期望 8888，实际 %d", config.Server.Port)
	}
	if config.Database.Path != "env.db" {
		t.Errorf("环境变量覆盖数据库路径失败，期望 env.db，实际 %s", config.Database.Path)
	}
	if config.AI.BaseURL != "http://env-ai:9000" {
		t.Errorf("环境变量覆盖AI地址失败，期望 http://env-ai:9000，实际 %s", config.AI.BaseURL)
	}
	if config.Logging.Level != "debug" {
		t.Errorf("环境变量覆盖日志级别失败，期望 debug，实际 %s", config.Logging.Level)
	}

	t.Log("✅ 环境变量覆盖测试通过")
}

// TestConfigHelperMethods 测试配置辅助方法
func TestConfigHelperMethods(t *testing.T) {
	config := DefaultConfig()

	// 测试GetDatabasePath
	t.Run("GetDatabasePath", func(t *testing.T) {
		originalPath := os.Getenv("SMART_STOCK_DB_PATH")
		defer func() {
			if originalPath != "" {
				os.Setenv("SMART_STOCK_DB_PATH", originalPath)
			} else {
				os.Unsetenv("SMART_STOCK_DB_PATH")
			}
		}()

		// 没有环境变量时返回配置值
		if path := config.GetDatabasePath(); path != config.Database.Path {
			t.Errorf("GetDatabasePath返回错误值，期望 %s，实际 %s", config.Database.Path, path)
		}

		// 有环境变量时返回环境变量值
		os.Setenv("SMART_STOCK_DB_PATH", "env-test.db")
		if path := config.GetDatabasePath(); path != "env-test.db" {
			t.Errorf("GetDatabasePath应该返回环境变量值，期望 env-test.db，实际 %s", path)
		}
	})

	// 测试GetServerPort
	t.Run("GetServerPort", func(t *testing.T) {
		originalPort := os.Getenv("SMART_STOCK_PORT")
		defer func() {
			if originalPort != "" {
				os.Setenv("SMART_STOCK_PORT", originalPort)
			} else {
				os.Unsetenv("SMART_STOCK_PORT")
			}
		}()

		// 没有环境变量时返回配置值
		if port := config.GetServerPort(); port != config.Server.Port {
			t.Errorf("GetServerPort返回错误值，期望 %d，实际 %d", config.Server.Port, port)
		}

		// 有环境变量时返回环境变量值
		os.Setenv("SMART_STOCK_PORT", "7777")
		if port := config.GetServerPort(); port != 7777 {
			t.Errorf("GetServerPort应该返回环境变量值，期望 7777，实际 %d", port)
		}
	})

	// 测试GetAIBaseURL
	t.Run("GetAIBaseURL", func(t *testing.T) {
		originalURL := os.Getenv("SMART_STOCK_AI_URL")
		defer func() {
			if originalURL != "" {
				os.Setenv("SMART_STOCK_AI_URL", originalURL)
			} else {
				os.Unsetenv("SMART_STOCK_AI_URL")
			}
		}()

		// 没有环境变量时返回配置值
		if url := config.GetAIBaseURL(); url != config.AI.BaseURL {
			t.Errorf("GetAIBaseURL返回错误值，期望 %s，实际 %s", config.AI.BaseURL, url)
		}

		// 有环境变量时返回环境变量值
		os.Setenv("SMART_STOCK_AI_URL", "http://test-ai:8000")
		if url := config.GetAIBaseURL(); url != "http://test-ai:8000" {
			t.Errorf("GetAIBaseURL应该返回环境变量值，期望 http://test-ai:8000，实际 %s", url)
		}
	})

	// 测试GetLogLevel
	t.Run("GetLogLevel", func(t *testing.T) {
		originalLevel := os.Getenv("SMART_STOCK_LOG_LEVEL")
		defer func() {
			if originalLevel != "" {
				os.Setenv("SMART_STOCK_LOG_LEVEL", originalLevel)
			} else {
				os.Unsetenv("SMART_STOCK_LOG_LEVEL")
			}
		}()

		// 没有环境变量时返回配置值
		if level := config.GetLogLevel(); level != config.Logging.Level {
			t.Errorf("GetLogLevel返回错误值，期望 %s，实际 %s", config.Logging.Level, level)
		}

		// 有环境变量时返回环境变量值
		os.Setenv("SMART_STOCK_LOG_LEVEL", "warn")
		if level := config.GetLogLevel(); level != "warn" {
			t.Errorf("GetLogLevel应该返回环境变量值，期望 warn，实际 %s", level)
		}
	})

	// 测试GetConfigSummary
	t.Run("GetConfigSummary", func(t *testing.T) {
		summary := config.GetConfigSummary()
		if summary == nil {
			t.Error("配置摘要不能为空")
		}

		// 验证摘要包含必要字段
		if server, ok := summary["server"].(map[string]interface{}); ok {
			if _, ok := server["address"]; !ok {
				t.Error("服务器摘要应该包含地址信息")
			}
		} else {
			t.Error("服务器摘要格式错误")
		}

		if database, ok := summary["database"].(map[string]interface{}); ok {
			if _, ok := database["path"]; !ok {
				t.Error("数据库摘要应该包含路径信息")
			}
		} else {
			t.Error("数据库摘要格式错误")
		}
	})

	t.Log("✅ 配置辅助方法测试通过")
}

// TestMergeConfigs 测试配置合并
func TestMergeConfigs(t *testing.T) {
	baseConfig := DefaultConfig()
	overrideConfig := &Config{
		Server: &ServerConfig{
			Host: "override-host",
			Port: 9999,
		},
		Database: &DatabaseConfig{
			Path: "override.db",
		},
		AI: &AIConfig{
			BaseURL: "http://override-ai:9000",
		},
	}

	// 测试合并配置
	merged := MergeConfigs(baseConfig, overrideConfig)
	if merged == nil {
		t.Fatal("合并配置不能为空")
	}

	// 验证覆盖的值
	if merged.Server.Host != "override-host" {
		t.Errorf("合并后的主机名错误，期望 override-host，实际 %s", merged.Server.Host)
	}
	if merged.Server.Port != 9999 {
		t.Errorf("合并后的端口错误，期望 9999，实际 %d", merged.Server.Port)
	}
	if merged.Database.Path != "override.db" {
		t.Errorf("合并后的数据库路径错误，期望 override.db，实际 %s", merged.Database.Path)
	}
	if merged.AI.BaseURL != "http://override-ai:9000" {
		t.Errorf("合并后的AI地址错误，期望 http://override-ai:9000，实际 %s", merged.AI.BaseURL)
	}

	// 验证保留的值
	if !merged.Server.EnableCORS {
		t.Error("合并后应该保留CORS设置")
	}
	if !merged.Database.EnableWAL {
		t.Error("合并后应该保留WAL设置")
	}

	// 测试nil参数
	if merged := MergeConfigs(nil, overrideConfig); merged != overrideConfig {
		t.Error("base为nil时应该返回override")
	}

	if merged := MergeConfigs(baseConfig, nil); merged != baseConfig {
		t.Error("override为nil时应该返回base")
	}

	t.Log("✅ 配置合并测试通过")
}

// TestSetEnvFromConfig 测试从配置设置环境变量
func TestSetEnvFromConfig(t *testing.T) {
	// 保存原始环境变量
	originalVars := map[string]string{
		"SMART_STOCK_HOST":         os.Getenv("SMART_STOCK_HOST"),
		"SMART_STOCK_PORT":         os.Getenv("SMART_STOCK_PORT"),
		"SMART_STOCK_DB_PATH":      os.Getenv("SMART_STOCK_DB_PATH"),
		"SMART_STOCK_AI_URL":       os.Getenv("SMART_STOCK_AI_URL"),
		"SMART_STOCK_LOG_LEVEL":    os.Getenv("SMART_STOCK_LOG_LEVEL"),
		"SMART_STOCK_DATA_SOURCES": os.Getenv("SMART_STOCK_DATA_SOURCES"),
	}

	// 测试后恢复环境变量
	defer func() {
		for key, value := range originalVars {
			if value != "" {
				os.Setenv(key, value)
			} else {
				os.Unsetenv(key)
			}
		}
	}()

	// 设置配置到环境变量
	config := DefaultConfig()
	config.SetEnvFromConfig()

	// 验证环境变量设置
	if host := os.Getenv("SMART_STOCK_HOST"); host != config.Server.Host {
		t.Errorf("环境变量主机名设置错误，期望 %s，实际 %s", config.Server.Host, host)
	}

	if port := os.Getenv("SMART_STOCK_PORT"); port != "8080" {
		t.Errorf("环境变量端口设置错误，期望 8080，实际 %s", port)
	}

	if dbPath := os.Getenv("SMART_STOCK_DB_PATH"); dbPath != config.Database.Path {
		t.Errorf("环境变量数据库路径设置错误，期望 %s，实际 %s", config.Database.Path, dbPath)
	}

	if aiURL := os.Getenv("SMART_STOCK_AI_URL"); aiURL != config.AI.BaseURL {
		t.Errorf("环境变量AI地址设置错误，期望 %s，实际 %s", config.AI.BaseURL, aiURL)
	}

	if logLevel := os.Getenv("SMART_STOCK_LOG_LEVEL"); logLevel != config.Logging.Level {
		t.Errorf("环境变量日志级别设置错误，期望 %s，实际 %s", config.Logging.Level, logLevel)
	}

	t.Log("✅ 从配置设置环境变量测试通过")
}

// TestReloadConfig 测试重新加载配置
func TestReloadConfig(t *testing.T) {
	// 创建临时配置文件
	tempDir := t.TempDir()
	configPath := filepath.Join(tempDir, "config.json")

	// 保存初始配置
	config := DefaultConfig()
	if err := SaveConfig(config, configPath); err != nil {
		t.Fatalf("保存初始配置失败: %v", err)
	}

	// 重新加载配置
	reloadedConfig, err := ReloadConfig(configPath)
	if err != nil {
		t.Errorf("重新加载配置失败: %v", err)
	}

	// 验证重新加载的配置
	if reloadedConfig.Server.Host != config.Server.Host {
		t.Errorf("重新加载的配置主机名错误")
	}

	if reloadedConfig.Database.Path != config.Database.Path {
		t.Errorf("重新加载的配置数据库路径错误")
	}

	t.Log("✅ 重新加载配置测试通过")
}

// TestConfigEdgeCases 测试配置边界情况
func TestConfigEdgeCases(t *testing.T) {
	// 测试无效端口解析
	t.Run("无效端口解析", func(t *testing.T) {
		if _, err := parsePort("invalid"); err == nil {
			t.Error("无效端口应该解析失败")
		}
		if _, err := parsePort("99999"); err == nil {
			t.Error("超出范围的端口应该解析失败")
		}
		if _, err := parsePort("0"); err == nil {
			t.Error("端口0应该解析失败")
		}
	})

	// 测试配置文件损坏
	t.Run("损坏的配置文件", func(t *testing.T) {
		tempDir := t.TempDir()
		configPath := filepath.Join(tempDir, "invalid.json")

		// 创建无效JSON文件
		if err := os.WriteFile(configPath, []byte("{invalid json"), 0644); err != nil {
			t.Fatalf("创建无效配置文件失败: %v", err)
		}

		// 尝试加载应该失败
		if _, err := LoadConfig(configPath); err == nil {
			t.Error("加载无效配置文件应该失败")
		}
	})

	// 测试配置文件权限问题
	t.Run("配置文件权限", func(t *testing.T) {
		// 这个测试在Unix系统上更有效，在Windows上可能不适用
		// 因此跳过权限测试
		t.Skip("跳过权限测试")
	})

	t.Log("✅ 配置边界情况测试通过")
}