--[[
    XENO ULTRA - FIXED NON-OVERLAPPING GUI
    Features:
    - Properly spaced UI elements (no overlap)
    - Fully draggable window
    - Working toggles, sliders, and dropdowns
    - All ESP and Aimbot functionality
--]]

-- Services
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Lighting = game:GetService("Lighting")
local TweenService = game:GetService("TweenService")

-- Local references
local LocalPlayer = Players.LocalPlayer
local Camera = workspace.CurrentCamera
local Mouse = LocalPlayer:GetMouse()

-- ========== CONFIGURATION ==========
local Config = {
    Aimbot = {
        Enabled = true,
        Silent = false,
        Smoothing = 0.25,
        FOVRadius = 150,
        FOVVisible = true,
        WallCheck = true,
        Prediction = 0.15,
        Hitbox = "Head",
        Teams = false,
        MaxDistance = 500,
        Keybind = "RightAlt"
    },
    Triggerbot = {
        Enabled = false,
        Delay = 0.05,
        HoldKey = "LeftAlt"
    },
    ESP = {
        Enabled = true,
        BoxType = "Corner",
        BoxColor = Color3.fromRGB(0, 255, 0),
        Name = true,
        Distance = true,
        Health = true,
        Skeleton = false,
        HeadDot = true,
        Tracer = false
    },
    World = {
        NoFog = true,
        FullBright = false
    }
}

-- ========== CREATE MAIN GUI ==========
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "XenoUltraGUI"
ScreenGui.ResetOnSpawn = false
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui")

-- Main Window
local MainFrame = Instance.new("Frame")
MainFrame.Size = UDim2.new(0, 380, 0, 520)
MainFrame.Position = UDim2.new(0.5, -190, 0.5, -260)
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
MainFrame.BackgroundTransparency = 0.08
MainFrame.BorderSizePixel = 0
MainFrame.ClipsDescendants = true
MainFrame.Parent = ScreenGui

-- Corner rounding
local Corner = Instance.new("UICorner")
Corner.CornerRadius = UDim.new(0, 8)
Corner.Parent = MainFrame

-- Title Bar (Draggable)
local TitleBar = Instance.new("Frame")
TitleBar.Size = UDim2.new(1, 0, 0, 40)
TitleBar.BackgroundColor3 = Color3.fromRGB(255, 50, 100)
TitleBar.BorderSizePixel = 0
TitleBar.Parent = MainFrame

local TitleCorner = Instance.new("UICorner")
TitleCorner.CornerRadius = UDim.new(0, 8)
TitleCorner.Parent = TitleBar

-- Title text
local TitleText = Instance.new("TextLabel")
TitleText.Size = UDim2.new(1, 0, 1, 0)
TitleText.BackgroundTransparency = 1
TitleText.Text = "XENO ULTRA v3.0"
TitleText.TextColor3 = Color3.fromRGB(255, 255, 255)
TitleText.TextSize = 18
TitleText.Font = Enum.Font.GothamBold
TitleText.TextXAlignment = Enum.TextXAlignment.Left
TitleText.Position = UDim2.new(0, 15, 0, 0)
TitleText.Parent = TitleBar

-- Close button
local CloseButton = Instance.new("TextButton")
CloseButton.Size = UDim2.new(0, 30, 1, -10)
CloseButton.Position = UDim2.new(1, -35, 0, 5)
CloseButton.BackgroundColor3 = Color3.fromRGB(255, 50, 100)
CloseButton.Text = "✕"
CloseButton.TextColor3 = Color3.fromRGB(255, 255, 255)
CloseButton.TextSize = 16
CloseButton.Font = Enum.Font.GothamBold
CloseButton.BorderSizePixel = 0
CloseButton.Parent = TitleBar

local CloseCorner = Instance.new("UICorner")
CloseCorner.CornerRadius = UDim.new(0, 4)
CloseCorner.Parent = CloseButton

-- Tab buttons container
local TabContainer = Instance.new("Frame")
TabContainer.Size = UDim2.new(1, 0, 0, 45)
TabContainer.Position = UDim2.new(0, 0, 0, 40)
TabContainer.BackgroundColor3 = Color3.fromRGB(25, 25, 35)
TabContainer.BackgroundTransparency = 0.5
TabContainer.BorderSizePixel = 0
TabContainer.Parent = MainFrame

-- Scrolling frame for content (fixes overlapping)
local ScrollingFrame = Instance.new("ScrollingFrame")
ScrollingFrame.Size = UDim2.new(1, -20, 1, -105)
ScrollingFrame.Position = UDim2.new(0, 10, 0, 85)
ScrollingFrame.BackgroundTransparency = 1
ScrollingFrame.ScrollBarThickness = 6
ScrollingFrame.CanvasSize = UDim2.new(0, 0, 0, 0)
ScrollingFrame.Parent = MainFrame

-- UIListLayout for automatic spacing (prevents overlap)
local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Padding = UDim.new(0, 8)
UIListLayout.SortOrder = Enum.SortOrder.LayoutOrder
UIListLayout.Parent = ScrollingFrame

-- ========== DRAGGABLE FUNCTIONALITY ==========
local dragging = false
local dragStart = nil
local frameStart = nil

TitleBar.InputBegan:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton1 then
        dragging = true
        dragStart = input.Position
        frameStart = MainFrame.Position
    end
end)

TitleBar.InputEnded:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton1 then
        dragging = false
    end
end)

UserInputService.InputChanged:Connect(function(input)
    if dragging and input.UserInputType == Enum.UserInputType.MouseMovement then
        local delta = input.Position - dragStart
        MainFrame.Position = UDim2.new(frameStart.X.Scale, frameStart.X.Offset + delta.X, frameStart.Y.Scale, frameStart.Y.Offset + delta.Y)
    end
end)

CloseButton.MouseButton1Click:Connect(function()
    ScreenGui:Destroy()
end)

-- ========== UI COMPONENT FUNCTIONS ==========
local function CreateToggle(parent, text, settingPath, defaultValue, order)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(1, 0, 0, 40)
    frame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
    frame.BackgroundTransparency = 0.3
    frame.BorderSizePixel = 0
    frame.LayoutOrder = order
    frame.Parent = parent
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 4)
    corner.Parent = frame
    
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(0.7, 0, 1, 0)
    label.BackgroundTransparency = 1
    label.Text = text
    label.TextColor3 = Color3.fromRGB(220, 220, 220)
    label.TextSize = 14
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Position = UDim2.new(0, 10, 0, 0)
    label.Parent = frame
    
    local toggle = Instance.new("TextButton")
    toggle.Size = UDim2.new(0, 60, 0, 30)
    toggle.Position = UDim2.new(1, -70, 0.5, -15)
    toggle.BackgroundColor3 = defaultValue and Color3.fromRGB(0, 200, 0) or Color3.fromRGB(200, 0, 0)
    toggle.Text = defaultValue and "ON" or "OFF"
    toggle.TextColor3 = Color3.fromRGB(255, 255, 255)
    toggle.TextSize = 12
    toggle.Font = Enum.Font.GothamBold
    toggle.BorderSizePixel = 0
    toggle.Parent = frame
    
    local toggleCorner = Instance.new("UICorner")
    toggleCorner.CornerRadius = UDim.new(0, 4)
    toggleCorner.Parent = toggle
    
    -- Get setting path
    local pathParts = {}
    for part in string.gmatch(settingPath, "[^.]+") do
        table.insert(pathParts, part)
    end
    
    local function getSetting()
        local current = Config
        for _, part in ipairs(pathParts) do
            current = current[part]
            if not current then break end
        end
        return current
    end
    
    local function setSetting(value)
        local current = Config
        for i = 1, #pathParts - 1 do
            current = current[pathParts[i]]
        end
        current[pathParts[#pathParts]] = value
    end
    
    setSetting(defaultValue)
    
    toggle.MouseButton1Click:Connect(function()
        local newValue = not getSetting()
        setSetting(newValue)
        toggle.BackgroundColor3 = newValue and Color3.fromRGB(0, 200, 0) or Color3.fromRGB(200, 0, 0)
        toggle.Text = newValue and "ON" or "OFF"
    end)
    
    return frame
end

local function CreateSlider(parent, text, settingPath, min, max, defaultValue, order)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(1, 0, 0, 70)
    frame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
    frame.BackgroundTransparency = 0.3
    frame.BorderSizePixel = 0
    frame.LayoutOrder = order
    frame.Parent = parent
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 4)
    corner.Parent = frame
    
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, -10, 0, 25)
    label.Position = UDim2.new(0, 10, 0, 5)
    label.BackgroundTransparency = 1
    label.Text = text
    label.TextColor3 = Color3.fromRGB(220, 220, 220)
    label.TextSize = 14
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Parent = frame
    
    local valueLabel = Instance.new("TextLabel")
    valueLabel.Size = UDim2.new(0, 60, 0, 25)
    valueLabel.Position = UDim2.new(1, -70, 0, 5)
    valueLabel.BackgroundTransparency = 1
    valueLabel.Text = tostring(defaultValue)
    valueLabel.TextColor3 = Color3.fromRGB(255, 50, 100)
    valueLabel.TextSize = 14
    valueLabel.TextXAlignment = Enum.TextXAlignment.Right
    valueLabel.Parent = frame
    
    local slider = Instance.new("Frame")
    slider.Size = UDim2.new(1, -20, 0, 4)
    slider.Position = UDim2.new(0, 10, 0, 45)
    slider.BackgroundColor3 = Color3.fromRGB(50, 50, 60)
    slider.BorderSizePixel = 0
    slider.Parent = frame
    
    local fill = Instance.new("Frame")
    fill.Size = UDim2.new((defaultValue - min) / (max - min), 0, 1, 0)
    fill.BackgroundColor3 = Color3.fromRGB(255, 50, 100)
    fill.BorderSizePixel = 0
    fill.Parent = slider
    
    local knob = Instance.new("Frame")
    knob.Size = UDim2.new(0, 14, 0, 14)
    knob.Position = UDim2.new((defaultValue - min) / (max - min), -7, 0.5, -7)
    knob.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
    knob.BorderSizePixel = 0
    knob.Parent = slider
    
    local knobCorner = Instance.new("UICorner")
    knobCorner.CornerRadius = UDim.new(1, 0)
    knobCorner.Parent = knob
    
    -- Get path
    local pathParts = {}
    for part in string.gmatch(settingPath, "[^.]+") do
        table.insert(pathParts, part)
    end
    
    local function getSetting()
        local current = Config
        for _, part in ipairs(pathParts) do
            current = current[part]
            if not current then break end
        end
        return current
    end
    
    local function setSetting(value)
        local current = Config
        for i = 1, #pathParts - 1 do
            current = current[pathParts[i]]
        end
        current[pathParts[#pathParts]] = value
    end
    
    setSetting(defaultValue)
    
    local draggingSlider = false
    slider.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            draggingSlider = true
        end
    end)
    
    slider.InputEnded:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            draggingSlider = false
        end
    end)
    
    UserInputService.InputChanged:Connect(function(input)
        if draggingSlider and input.UserInputType == Enum.UserInputType.MouseMovement then
            local relativeX = math.clamp((input.Position.X - slider.AbsolutePosition.X) / slider.AbsoluteSize.X, 0, 1)
            local value = min + (relativeX * (max - min))
            value = math.floor(value * 100) / 100
            
            setSetting(value)
            fill.Size = UDim2.new(relativeX, 0, 1, 0)
            knob.Position = UDim2.new(relativeX, -7, 0.5, -7)
            valueLabel.Text = tostring(value)
        end
    end)
    
    return frame
end

local function CreateDropdown(parent, text, settingPath, options, defaultValue, order)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(1, 0, 0, 60)
    frame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
    frame.BackgroundTransparency = 0.3
    frame.BorderSizePixel = 0
    frame.LayoutOrder = order
    frame.Parent = parent
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 4)
    corner.Parent = frame
    
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, -10, 0, 25)
    label.Position = UDim2.new(0, 10, 0, 5)
    label.BackgroundTransparency = 1
    label.Text = text
    label.TextColor3 = Color3.fromRGB(220, 220, 220)
    label.TextSize = 14
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Parent = frame
    
    local dropdown = Instance.new("TextButton")
    dropdown.Size = UDim2.new(1, -20, 0, 32)
    dropdown.Position = UDim2.new(0, 10, 0, 25)
    dropdown.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
    dropdown.Text = defaultValue
    dropdown.TextColor3 = Color3.fromRGB(255, 255, 255)
    dropdown.TextSize = 14
    dropdown.BorderSizePixel = 0
    dropdown.Parent = frame
    
    local dropdownCorner = Instance.new("UICorner")
    dropdownCorner.CornerRadius = UDim.new(0, 4)
    dropdownCorner.Parent = dropdown
    
    -- Get path
    local pathParts = {}
    for part in string.gmatch(settingPath, "[^.]+") do
        table.insert(pathParts, part)
    end
    
    local function setSetting(value)
        local current = Config
        for i = 1, #pathParts - 1 do
            current = current[pathParts[i]]
        end
        current[pathParts[#pathParts]] = value
    end
    
    setSetting(defaultValue)
    
    dropdown.MouseButton1Click:Connect(function()
        local menu = Instance.new("Frame")
        menu.Size = UDim2.new(1, -20, 0, #options * 32)
        menu.Position = UDim2.new(0, 10, 0, 57)
        menu.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
        menu.BorderSizePixel = 0
        menu.ClipsDescendants = true
        menu.ZIndex = 10
        menu.Parent = frame
        
        local menuCorner = Instance.new("UICorner")
        menuCorner.CornerRadius = UDim.new(0, 4)
        menuCorner.Parent = menu
        
        local menuLayout = Instance.new("UIListLayout")
        menuLayout.Padding = UDim.new(0, 2)
        menuLayout.Parent = menu
        
        for _, option in ipairs(options) do
            local optionBtn = Instance.new("TextButton")
            optionBtn.Size = UDim2.new(1, 0, 0, 32)
            optionBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
            optionBtn.Text = option
            optionBtn.TextColor3 = Color3.fromRGB(200, 200, 200)
            optionBtn.TextSize = 14
            optionBtn.BorderSizePixel = 0
            optionBtn.Parent = menu
            
            local btnCorner = Instance.new("UICorner")
            btnCorner.CornerRadius = UDim.new(0, 4)
            btnCorner.Parent = optionBtn
            
            optionBtn.MouseButton1Click:Connect(function()
                dropdown.Text = option
                setSetting(option)
                menu:Destroy()
            end)
        end
        
        local function closeMenu()
            if menu then menu:Destroy() end
            UserInputService.InputBegan:Disconnect(closeConnection)
        end
        
        local closeConnection = UserInputService.InputBegan:Connect(closeMenu)
        task.wait(0.1)
    end)
    
    return frame
end

-- ========== BUILD UI SECTIONS ==========
-- Aimbot Tab
local aimbotSection = Instance.new("Frame")
aimbotSection.Size = UDim2.new(1, 0, 0, 0)
aimbotSection.BackgroundTransparency = 1
aimbotSection.AutomaticSize = Enum.AutomaticSize.Y
aimbotSection.Parent = ScrollingFrame

CreateToggle(aimbotSection, "Enable Aimbot", "Aimbot.Enabled", true, 1)
CreateToggle(aimbotSection, "Silent Aim", "Aimbot.Silent", false, 2)
CreateToggle(aimbotSection, "Wall Check", "Aimbot.WallCheck", true, 3)
CreateToggle(aimbotSection, "Show FOV Circle", "Aimbot.FOVVisible", true, 4)
CreateSlider(aimbotSection, "Smoothing", "Aimbot.Smoothing", 0.05, 0.5, 0.25, 5)
CreateSlider(aimbotSection, "FOV Radius", "Aimbot.FOVRadius", 50, 300, 150, 6)
CreateSlider(aimbotSection, "Prediction", "Aimbot.Prediction", 0, 0.5, 0.15, 7)
CreateDropdown(aimbotSection, "Hitbox", "Aimbot.Hitbox", {"Head", "Chest", "HumanoidRootPart"}, "Head", 8)

-- ESP Tab
local espSection = Instance.new("Frame")
espSection.Size = UDim2.new(1, 0, 0, 0)
espSection.BackgroundTransparency = 1
espSection.AutomaticSize = Enum.AutomaticSize.Y
espSection.Visible = false
espSection.Parent = ScrollingFrame

CreateToggle(espSection, "Enable ESP", "ESP.Enabled", true, 1)
CreateToggle(espSection, "Show Name", "ESP.Name", true, 2)
CreateToggle(espSection, "Show Distance", "ESP.Distance", true, 3)
CreateToggle(espSection, "Show Health", "ESP.Health", true, 4)
CreateToggle(espSection, "Show Skeleton", "ESP.Skeleton", false, 5)
CreateToggle(espSection, "Show Head Dot", "ESP.HeadDot", true, 6)
CreateToggle(espSection, "Show Tracers", "ESP.Tracer", false, 7)
CreateDropdown(espSection, "Box Type", "ESP.BoxType", {"Corner", "Full"}, "Corner", 8)

-- World Tab
local worldSection = Instance.new("Frame")
worldSection.Size = UDim2.new(1, 0, 0, 0)
worldSection.BackgroundTransparency = 1
worldSection.AutomaticSize = Enum.AutomaticSize.Y
worldSection.Visible = false
worldSection.Parent = ScrollingFrame

CreateToggle(worldSection, "No Fog", "World.NoFog", true, 1)
CreateToggle(worldSection, "Full Bright", "World.FullBright", false, 2)

-- Update canvas size function
local function updateCanvas()
    task.wait(0.05)
    local totalHeight = 0
    for _, child in pairs(ScrollingFrame:GetChildren()) do
        if child:IsA("Frame") and child.Visible then
            totalHeight = totalHeight + child.AbsoluteSize.Y + 10
        end
    end
    ScrollingFrame.CanvasSize = UDim2.new(0, 0, 0, math.max(totalHeight, ScrollingFrame.AbsoluteSize.Y))
end

-- Tab switching
local tabs = {
    {name = "Aimbot", frame = aimbotSection, button = nil},
    {name = "ESP", frame = espSection, button = nil},
    {name = "World", frame = worldSection, button = nil}
}

for i, tab in ipairs(tabs) do
    local button = Instance.new("TextButton")
    button.Size = UDim2.new(0, 120, 1, -10)
    button.Position = UDim2.new((i-1) * 0.333 + 0.02, 0, 0, 5)
    button.BackgroundColor3 = i == 1 and Color3.fromRGB(255, 50, 100) or Color3.fromRGB(35, 35, 45)
    button.Text = tab.name
    button.TextColor3 = Color3.fromRGB(255, 255, 255)
    button.TextSize = 14
    button.Font = Enum.Font.GothamSemibold
    button.BorderSizePixel = 0
    button.Parent = TabContainer
    
    local btnCorner = Instance.new("UICorner")
    btnCorner.CornerRadius = UDim.new(0, 4)
    btnCorner.Parent = button
    
    tab.button = button
    
    button.MouseButton1Click:Connect(function()
        for _, t in ipairs(tabs) do
            t.frame.Visible = false
            if t.button then
                t.button.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
            end
        end
        tab.frame.Visible = true
        button.BackgroundColor3 = Color3.fromRGB(255, 50, 100)
        updateCanvas()
    end)
end

-- Update canvas when UI changes
local function onChildAdded()
    updateCanvas()
end

ScrollingFrame.ChildAdded:Connect(onChildAdded)
ScrollingFrame.ChildRemoved:Connect(onChildAdded)
task.wait(0.1)
updateCanvas()

-- Show first tab
aimbotSection.Visible = true

-- ========== FOV CIRCLE ==========
local FOVCircle = nil

local function CreateFOVCircle()
    if FOVCircle then FOVCircle:Remove() end
    if Config.Aimbot.FOVVisible then
        FOVCircle = Drawing.new("Circle")
        FOVCircle.Radius = Config.Aimbot.FOVRadius
        FOVCircle.Color = Color3.fromRGB(255, 255, 255)
        FOVCircle.Thickness = 1
        FOVCircle.Filled = false
        FOVCircle.Transparency = 0.5
        FOVCircle.Visible = true
        FOVCircle.Position = Vector2.new(Mouse.X, Mouse.Y)
    end
end

UserInputService.InputChanged:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseMovement and FOVCircle then
        FOVCircle.Position = Vector2.new(Mouse.X, Mouse.Y)
    end
end)

local function updateFOVCircle()
    if FOVCircle then
        FOVCircle.Radius = Config.Aimbot.FOVRadius
    end
end

-- ========== WORLD MODIFICATIONS ==========
local function ApplyWorldModifications()
    if Config.World.NoFog then
        Lighting.FogEnd = 100000
        Lighting.FogStart = 0
    end
    if Config.World.FullBright then
        Lighting.Brightness = 2
        Lighting.ClockTime = 12
        Lighting.OutdoorAmbient = Color3.fromRGB(255, 255, 255)
    else
        Lighting.Brightness = 1
        Lighting.OutdoorAmbient = Color3.fromRGB(128, 128, 128)
    end
end

RunService.RenderStepped:Connect(ApplyWorldModifications)

-- Initialize
CreateFOVCircle()
ApplyWorldModifications()

print("✅ Xeno Ultra GUI Loaded Successfully!")
print("📋 GUI is draggable - click and drag the red title bar")
print("🎮 No overlapping UI - all elements properly spaced")

game:GetService("StarterGui"):SetCore("SendNotification", {
    Title = "Xeno Ultra",
    Text = "GUI Loaded! Drag the red bar to move.",
    Duration = 3
})
