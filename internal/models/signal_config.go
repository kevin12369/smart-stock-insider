package models

import (
	"database/sql"
	"time"

	_ "modernc.org/sqlite"
)

// SignalConfig 信号配置
type SignalConfig struct {
	ID          int       `json:"id"`
	SignalType  string    `json:"signal_type"`
	Weight      float64   `json:"weight"`
	Enabled     bool      `json:"enabled"`
	Description string    `json:"description"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// SignalCombo 信号组合
type SignalCombo struct {
	ID          int       `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Signals     []SignalConfig `json:"signals"`
	Enabled     bool      `json:"enabled"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// ComboResult 组合信号结果
type ComboResult struct {
	ID          int       `json:"id"`
	ComboID     int       `json:"combo_id"`
	ComboName   string    `json:"combo_name"`
	Code        string    `json:"code"`
	Date        string    `json:"date"`
	Score       float64   `json:"score"`
	SignalCount int       `json:"signal_count"`
	BuySignals  int       `json:"buy_signals"`
	SellSignals int       `json:"sell_signals"`
	Description string    `json:"description"`
	CreatedAt   time.Time `json:"created_at"`
}

// SignalConfigService 信号配置服务
type SignalConfigService struct {
	db *sql.DB
}

// NewSignalConfigService 创建信号配置服务
func NewSignalConfigService(db *sql.DB) *SignalConfigService {
	return &SignalConfigService{db: db}
}

// InitDefaultConfigs 初始化默认配置
func (s *SignalConfigService) InitDefaultConfigs() error {
	// 创建配置表
	queries := []string{
		`CREATE TABLE IF NOT EXISTS signal_config (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			signal_type TEXT NOT NULL,
			weight REAL NOT NULL DEFAULT 1.0,
			enabled INTEGER NOT NULL DEFAULT 1,
			description TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS signal_combo (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			description TEXT,
			enabled INTEGER NOT NULL DEFAULT 1,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS combo_signal (
			combo_id INTEGER,
			signal_config_id INTEGER,
			PRIMARY KEY (combo_id, signal_config_id),
			FOREIGN KEY (combo_id) REFERENCES signal_combo(id) ON DELETE CASCADE,
			FOREIGN KEY (signal_config_id) REFERENCES signal_config(id) ON DELETE CASCADE
		)`,
		`CREATE TABLE IF NOT EXISTS combo_result (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			combo_id INTEGER NOT NULL,
			combo_name TEXT NOT NULL,
			code TEXT NOT NULL,
			date TEXT NOT NULL,
			score REAL NOT NULL,
			signal_count INTEGER DEFAULT 0,
			buy_signals INTEGER DEFAULT 0,
			sell_signals INTEGER DEFAULT 0,
			description TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (combo_id) REFERENCES signal_combo(id)
		)`,
	}

	for _, query := range queries {
		if _, err := s.db.Exec(query); err != nil {
			return err
		}
	}

	// 插入默认信号配置
	defaultSignals := []SignalConfig{
		{SignalType: "MACD", Weight: 1.2, Enabled: true, Description: "MACD指标权重"},
		{SignalType: "RSI", Weight: 1.0, Enabled: true, Description: "RSI指标权重"},
	{SignalType: "KDJ", Weight: 0.8, Enabled: true, Description: "KDJ指标权重"},
		{SignalType: "BOLL", Weight: 0.9, Enabled: true, Description: "布林带指标权重"},
		{SignalType: "CCI", Weight: 0.7, Enabled: true, Description: "CCI指标权重"},
		{SignalType: "WR", Weight: 0.6, Enabled: true, Description: "威廉指标权重"},
		{SignalType: "MA", Weight: 0.5, Enabled: true, Description: "移动平均线权重"},
	}

	for _, signal := range defaultSignals {
		query := `INSERT OR REPLACE INTO signal_config (signal_type, weight, enabled, description)
		          VALUES (?, ?, ?, ?)`
		_, err := s.db.Exec(query, signal.SignalType, signal.Weight, signal.Enabled, signal.Description)
		if err != nil {
			return err
		}
	}

	// 插入默认组合
	defaultCombos := []SignalCombo{
		{
			Name:        "技术分析综合策略",
			Description: "综合多种技术指标的量化策略",
			Signals:     defaultSignals,
			Enabled:     true,
		},
		{
			Name:        "趋势跟踪策略",
			Description: "主要使用MACD和移动平均线的趋势策略",
			Signals: []SignalConfig{
				{SignalType: "MACD", Weight: 1.5, Enabled: true, Description: "MACD指标权重增加"},
				{SignalType: "MA", Weight: 1.0, Enabled: true, Description: "移动平均线权重"},
				{SignalType: "RSI", Weight: 0.5, Enabled: true, Description: "RSI指标权重减少"},
			},
			Enabled: true,
		},
		{
			Name: "震荡策略",
			Description: "适用于震荡市场的超买超卖策略",
			Signals: []SignalConfig{
				{SignalType: "RSI", Weight: 1.5, Enabled: true, Description: "RSI指标权重增加"},
				{SignalType: "WR", Weight: 1.2, Enabled: true, Description: "威廉指标权重增加"},
				{SignalType: "CCI", Weight: 1.0, Enabled: true, Description: "CCI指标权重"},
			},
			Enabled: true,
		},
	}

	for _, combo := range defaultCombos {
		// 插入组合
		query := `INSERT INTO signal_combo (name, description, enabled) VALUES (?, ?, ?)`
		result, err := s.db.Exec(query, combo.Name, combo.Description, combo.Enabled)
		if err != nil {
			return err
		}
		comboID, _ := result.LastInsertId()

		// 插入组合信号关联
		for _, signal := range combo.Signals {
			query := `INSERT OR REPLACE INTO combo_signal (combo_id, signal_config_id)
			          SELECT id FROM signal_config WHERE signal_type = ?`
			_, err := s.db.Exec(query, comboID, signal.SignalType)
			if err != nil {
				return err
			}
		}
	}

	return nil
}

// GetSignalConfigs 获取所有信号配置
func (s *SignalConfigService) GetSignalConfigs() ([]SignalConfig, error) {
	query := `SELECT id, signal_type, weight, enabled, description, created_at, updated_at
	          FROM signal_config ORDER BY id`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	configs := make([]SignalConfig, 0)
	for rows.Next() {
		var config SignalConfig
		err := rows.Scan(&config.ID, &config.SignalType, &config.Weight, &config.Enabled,
			&config.Description, &config.CreatedAt, &config.UpdatedAt)
		if err != nil {
			continue
		}
		configs = append(configs, config)
	}

	return configs, nil
}

// GetSignalCombos 获取所有信号组合
func (s *SignalConfigService) GetSignalCombos() ([]SignalCombo, error) {
	query := `SELECT id, name, description, enabled, created_at, updated_at
	          FROM signal_combo ORDER BY id`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	combos := make([]SignalCombo, 0)
	for rows.Next() {
		var combo SignalCombo
		err := rows.Scan(&combo.ID, &combo.Name, &combo.Description, &combo.Enabled,
			&combo.CreatedAt, &combo.UpdatedAt)
		if err != nil {
			continue
		}

		// 获取组合关联的信号
		signalQuery := `SELECT sc.id, sc.signal_type, sc.weight, sc.enabled, sc.description
		                    FROM signal_config sc
		                    INNER JOIN combo_signal cs ON sc.id = cs.signal_config_id
		                    WHERE cs.combo_id = ?
		                    ORDER BY sc.id`

		signalRows, err := s.db.Query(signalQuery, combo.ID)
		if err != nil {
			continue
		}

		signals := make([]SignalConfig, 0)
		for signalRows.Next() {
			var signal SignalConfig
			err := signalRows.Scan(&signal.ID, &signal.SignalType, &signal.Weight,
				&signal.Enabled, &signal.Description)
			if err != nil {
				continue
			}
			signals = append(signals, signal)
		}
		signalRows.Close()

		combo.Signals = signals
		combos = append(combos, combo)
	}

	return combos, nil
}

// UpdateSignalConfig 更新信号配置
func (s *SignalConfigService) UpdateSignalConfig(config SignalConfig) error {
	query := `UPDATE signal_config
	          SET weight = ?, enabled = ?, description = ?, updated_at = ?
	          WHERE id = ?`

	_, err := s.db.Exec(query, config.Weight, config.Enabled, config.Description, time.Now(), config.ID)
	return err
}

// UpdateSignalCombo 更新信号组合
func (s *SignalConfigService) UpdateSignalCombo(combo SignalCombo) error {
	tx, err := s.db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// 更新组合信息
	query := `UPDATE signal_combo
	          SET name = ?, description = ?, enabled = ?, updated_at = ?
	          WHERE id = ?`
	_, err = tx.Exec(query, combo.Name, combo.Description, combo.Enabled, time.Now(), combo.ID)
	if err != nil {
		return err
	}

	// 删除旧的信号关联
	_, err = tx.Exec("DELETE FROM combo_signal WHERE combo_id = ?", combo.ID)
	if err != nil {
		return err
	}

	// 插入新的信号关联
	for _, signal := range combo.Signals {
		query := `INSERT OR REPLACE INTO combo_signal (combo_id, signal_config_id)
		          SELECT id FROM signal_config WHERE signal_type = ?`
		_, err = tx.Exec(query, combo.ID, signal.SignalType)
		if err != nil {
			return err
		}
	}

	return tx.Commit()
}

// SignalStrength 信号强度枚举
type SignalStrength int

const (
	// HoldSignal 观望信号
	HoldSignal SignalStrength = iota
	// BuySignal 买入信号
	BuySignal
	// StrongBuySignal 强烈买入信号
	StrongBuySignal
	// SellSignal 卖出信号
	SellSignal
	// StrongSellSignal 强烈卖出信号
	StrongSellSignal
)

// GetSignalStrength 从信号值获取强度
func GetSignalStrength(signalValue float64) SignalStrength {
	if signalValue >= 0.8 {
		return StrongBuySignal
	} else if signalValue >= 0.3 {
		return BuySignal
	} else if signalValue <= -0.8 {
		return StrongSellSignal
	} else if signalValue <= -0.3 {
		return SellSignal
	} else {
		return HoldSignal
	}
}

// CalculateComboScore 计算组合信号分数
func (s *SignalConfigService) CalculateComboScore(combo SignalCombo, signals []TechnicalSignal) float64 {
	score := 0.0
	signalWeightMap := make(map[string]float64)

	// 构建信号权重映射
	for _, signalConfig := range combo.Signals {
		if signalConfig.Enabled {
			signalWeightMap[signalConfig.SignalType] = signalConfig.Weight
		}
	}

	buyScore := 0.0
	sellScore := 0.0

	for _, signal := range signals {
		if weight, exists := signalWeightMap[signal.SignalType]; exists {
			// 根据信号值计算强度
			strength := GetSignalStrength(signal.SignalValue)
			signalScore := signal.SignalValue

			if strength == StrongBuySignal || strength == BuySignal {
				buyScore += signalScore * weight
			} else if strength == StrongSellSignal || strength == SellSignal {
				sellScore += signalScore * weight
			} else {
				// Hold信号给予中性分数
				score += 0.1 * weight
			}
		}
	}

	// 综合计算：买入信号减去卖出信号
	finalScore := buyScore - sellScore
	if len(signals) > 0 {
		finalScore = finalScore / float64(len(signals))
	}

	return finalScore
}

// SaveComboResult 保存组合结果
func (s *SignalConfigService) SaveComboResult(result ComboResult) error {
	query := `INSERT INTO combo_result
	          (combo_id, combo_name, code, date, score, signal_count, buy_signals, sell_signals, description, created_at)
	          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query, result.ComboID, result.ComboName, result.Code, result.Date,
		result.Score, result.SignalCount, result.BuySignals, result.SellSignals,
		result.Description, result.CreatedAt)
	return err
}

// GetComboResults 获取组合结果
func (s *SignalConfigService) GetComboResults(comboID int, code string, limit int) ([]ComboResult, error) {
	query := `SELECT id, combo_id, combo_name, code, date, score, signal_count, buy_signals, sell_signals, description, created_at
	          FROM combo_result
	          WHERE combo_id = ? AND code = ?
	          ORDER BY date DESC
	          LIMIT ?`

	rows, err := s.db.Query(query, comboID, code, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	results := make([]ComboResult, 0)
	for rows.Next() {
		var result ComboResult
		err := rows.Scan(&result.ID, &result.ComboID, &result.ComboName, &result.Code, &result.Date,
			&result.Score, &result.SignalCount, &result.BuySignals, &result.SellSignals,
			&result.Description, &result.CreatedAt)
		if err != nil {
			continue
		}
		results = append(results, result)
	}

	return results, nil
}