---
name: homework-writer
description: 快速生成大学文档作业内容（创业计划书、调研报告、实验报告、课程论文等），支持直接输出彩色PDF。当用户提到“水作业”、“写作业”、“文档作业”、“计划书”、“实验报告”、“导出PDF”或上传了作业模板文件（docx/pdf）时使用此技能。自动解析模板结构，根据用户主题和字数要求生成完整文档内容，支持标题着色、插入示意图、Word COM自动化导出PDF。
---

# 水文档作业 Skill

帮助用户快速完成各类大学文档作业，包括创业计划书、调研报告、实验报告、课程论文等。

## 核心流程

### Step 1: 获取模板与需求

1. 检查工作区中是否有用户提供的模板文件（.docx / .pdf / .txt）
2. 若有模板，提取其结构：
   - `.docx`：复制为 `.zip` 后解压，读取 `word/document.xml`，提取标题层级和占位提示
   - `.pdf`：尝试直接读取，若失败提示用户转换格式
   - `.txt`：直接读取
3. 若无模板，询问用户作业类型，使用通用结构（见下方模板库）

**提取模板结构的 PowerShell 命令：**
```powershell
Copy-Item "模板.docx" "temp.zip"
Expand-Archive -Path "temp.zip" -DestinationPath "docx_extracted" -Force
# 然后读取 docx_extracted/word/document.xml
```

**解析 XML 时的关键标签：**
- `<w:pStyle w:val="2"/>` → 一级标题（如"一、项目概述"）
- `<w:pStyle w:val="3"/>` → 二级标题（如"1.1 项目名称"）
- `<w:pStyle w:val="4"/>` → 三级标题
- `<w:t>文本内容</w:t>` → 段落文本

### Step 2: 确认作业信息

使用 AskUserQuestion 收集以下信息：
- **作业类型**：创业计划书 / 调研报告 / 实验报告 / 课程论文 / 其他
- **主题方向**：用户指定的具体主题或方向
- **字数要求**：3000-5000字 / 5000-8000字 / 8000字以上
- **特殊要求**：是否有特定的格式、数据、案例要求

### Step 3: 生成内容

根据模板结构逐节填充内容，遵循以下原则：

**内容质量标准：**
- 每节内容紧扣主题，避免空话套话
- 数据引用要合理（可编造但要逻辑自洽，如"根据XX报告显示..."）
- 团队人员用常见姓名，信息真实可信
- 财务数据要有基本的数学逻辑（收支要能对上）
- SWOT分析、竞争分析等框架要有实质内容
- 时间线从当前年份开始，规划合理

**"水"的技巧：**
- 背景部分：从大环境讲到具体痛点，层层递进
- 分析部分：多角度展开，每个点都写2-3句说明
- 策略部分：分点列举，条理清晰显得专业
- 风险部分：正反面都要写到，显得全面

**字数控制：**
- 3000字：每节150-300字，重点突出
- 5000字：每节200-400字，适当展开
- 8000字+：每节300-600字，详细论述，增加子章节

### Step 4: 输出文档

**优先输出 .docx 文件**（直接可用，无需手动复制）。

#### 4a. 基于模板生成 .docx 的流程

1. **解压模板**：
```powershell
Copy-Item "模板.docx" "temp.zip"
Expand-Archive -Path "temp.zip" -DestinationPath "docx_extracted" -Force
```

2. **读取模板 styles.xml**，确认标题样式ID映射（通常为）：
   - `w:val="2"` → 标题1（文档大标题）
   - `w:val="3"` → 标题2（一级标题，如"一、项目概述"）
   - `w:val="4"` → 标题3（二级标题，如"1.1 项目名称"）
   - 无样式 → 正文段落

3. **生成 document.xml**，使用以下 XML 模板：

**标题1（文档大标题）**：
```xml
<w:p w14:paraId="XXXXXXXX"><w:pPr><w:pStyle w:val="2"/></w:pPr><w:r><w:t>标题文本</w:t></w:r></w:p>
```

**一级标题（标题2）**：
```xml
<w:p w14:paraId="XXXXXXXX"><w:pPr><w:pStyle w:val="3"/></w:pPr><w:r><w:t>一、章节名</w:t></w:r></w:p>
```

**二级标题（标题3）**：
```xml
<w:p w14:paraId="XXXXXXXX"><w:pPr><w:pStyle w:val="4"/></w:pPr><w:r><w:t>1.1 小节名</w:t></w:r></w:p>
```

**正文段落**：
```xml
<w:p w14:paraId="XXXXXXXX"><w:r><w:t>正文内容</w:t></w:r></w:p>
```

**document.xml 完整结构**：
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
  ... (保留模板的完整命名空间)>
<w:body>
  <!-- 所有段落 -->
  <w:p w14:paraId="XXXXXXXX"/>
  <w:sectPr>...</w:sectPr>  <!-- 保留模板的页面设置 -->
</w:body></w:document>
```

**注意**：每个 `paraId` 必须是8位十六进制的唯一ID。

4. **替换 document.xml 并打包**：
```powershell
# 用生成的 document.xml 覆盖 docx_extracted/word/document.xml
Remove-Item "temp.zip" -Force
Compress-Archive -Path "docx_extracted\*" -DestinationPath "temp.zip" -Force
Copy-Item "temp.zip" "输出文件名.docx" -Force
```

#### 4b. 备用：输出 .txt 文件

如果无法生成 .docx（如无模板），退而输出 `.txt` 文件：
- 命名规则：`{文档类型}_{主题关键词}.txt`
- 标题层级用换行和编号清晰标识
- 每个章节之间空一行
- 数据表格用文字描述（用户自行转为Word表格）

#### 4c. 颜色 + 图片 + PDF 导出（Word COM 自动化）

当用户需要颜色设计、插入图片或直接导出 PDF 时，使用 Word COM 自动化：

**1. 生成示意图**（用 PowerShell System.Drawing）：
```powershell
Add-Type -AssemblyName System.Drawing
# 用 Draw-Box, Draw-Arrow 等函数绘制流程图/架构图/SWOT图
# 保存为 PNG 到 images/ 目录
```
注意：.ps1 文件必须用 **UTF-8 BOM** 编码保存，否则中文会乱码。

**2. Word COM 自动化脚本模板**：
```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false; $word.DisplayAlerts = 0
$doc = $word.Documents.Open($templatePath)

# 标题着色（Word 用 BGR 格式：R + G*256 + B*65536）
foreach ($para in $doc.Paragraphs) {
    $sn = $para.Style.NameLocal
    if ($sn -match "标题 1" -or $sn -eq "heading 1") {
        $para.Range.Font.Color = 53 + 107*256 + 255*65536  # 橙色
    }
    elseif ($sn -match "标题 2" -or $sn -eq "heading 2") {
        $para.Range.Font.Color = 182 + 196*256 + 46*65536  # 青色
    }
}

# 替换占位符文本
foreach ($para in $doc.Paragraphs) {
    if ($para.Range.Text.Trim() -eq "（占位符文本）") {
        $para.Range.Text = "实际内容"
    }
}

# 插入图片（找到标题后的段落末尾插入）
$range = $nextPara.Range
$range.Collapse(0)  # wdCollapseEnd
$range.InlineShapes.AddPicture($imagePath)

# 导出 PDF
$doc.ExportAsFixedFormat($pdfPath, 17)  # 17 = wdExportFormatPDF
$doc.Close($false); $word.Quit()
```

**关键注意事项**：
- Word 颜色用 **BGR 格式**：`R + G*256 + B*65536`
- .ps1 文件必须用 **UTF-8 BOM** 编码：`[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($true))`
- 替换文本时匹配 `$para.Range.Text.Trim()` 与占位符完全相等
- 图片插入用 `$range.Collapse(0)` 定位到段落末尾

## 通用模板库

### 创业计划书

```
一、项目概述（项目名称、背景、目标、团队）
二、市场分析（目标市场、竞争分析、SWOT分析）
三、产品/服务介绍（概述、技术实现、用户体验）
四、营销策略（定价、推广、销售）
五、运营计划（生产流程、供应链、客户服务）
六、财务计划（初始投资、收入预测、成本预测、盈亏平衡）
七、风险评估与应对措施
八、项目实施时间表
九、附录
```

### 调研报告

```
一、调研背景与目的
二、调研方法与设计（调研对象、样本量、问卷设计）
三、数据分析与结果（描述性统计、交叉分析、关键发现）
四、问题与讨论
五、结论与建议
六、附录（问卷原文、原始数据）
```

### 实验报告

```
一、实验目的
二、实验原理
三、实验设备与材料
四、实验步骤
五、实验数据与结果（数据记录表、计算过程、结果分析）
六、讨论与误差分析
七、结论
八、思考题
```

### 课程论文

```
摘要与关键词
一、引言（研究背景、研究意义、文献综述）
二、研究内容与方法
三、分析/设计/实现
四、结果与讨论
五、结论与展望
参考文献
```

## 注意事项

1. 如果用户上传了**优秀案例**，优先参考案例的风格、深度和篇幅
2. 生成内容后主动询问用户是否需要修改某个章节
3. 如果用户需要修改特定章节，只重新生成该章节内容
4. 提醒用户检查并替换占位信息（如姓名、学校等）
5. 建议用户用生成内容替换Word模板中的对应位置
6. 若用户需要PDF导出，确认系统已安装 Word（通过 `$word = New-Object -ComObject Word.Application; $word.Version` 检测）
7. 生成 .ps1 脚本后务必用 UTF-8 BOM 编码重新保存再执行
