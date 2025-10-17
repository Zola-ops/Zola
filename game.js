// 游戏状态
let gameState = {
    isPlaying: false,
    currentLevel: 1,
    unlockedLevels: [1],
    score: 0,
    bird: {
        y: 300,
        velocity: 0,
        gravity: 0.5,
        jumpForce: -10
    },
    obstacles: [],
    gameSpeed: 2,
    obstacleInterval: 1500,
    lastObstacleTime: 0
};

// DOM元素
const startScreen = document.getElementById('start-screen');
const levelScreen = document.getElementById('level-screen');
const gameScreen = document.getElementById('game-screen');
const gameOverScreen = document.getElementById('game-over-screen');
const startBtn = document.getElementById('start-btn');
const levelButtons = document.querySelectorAll('.level-btn');
const restartBtn = document.getElementById('restart-btn');
const bird = document.getElementById('bird');
const scoreDisplay = document.getElementById('score');
const finalScoreDisplay = document.getElementById('final-score');

// 事件监听
startBtn.addEventListener('click', showLevelScreen);
restartBtn.addEventListener('click', restartGame);
levelButtons.forEach(btn => {
    btn.addEventListener('click', () => startGame(parseInt(btn.dataset.level)));
});
document.addEventListener('click', jump);

// 显示关卡选择界面
function showLevelScreen() {
    startScreen.classList.add('hidden');
    levelScreen.classList.remove('hidden');
    
    // 更新解锁的关卡按钮
    levelButtons.forEach(btn => {
        const level = parseInt(btn.dataset.level);
        btn.disabled = !gameState.unlockedLevels.includes(level);
    });
}

// 开始游戏
function startGame(level) {
    gameState.currentLevel = level;
    gameState.isPlaying = true;
    gameState.score = 0;
    gameState.obstacles = [];
    gameState.bird.y = 300;
    gameState.bird.velocity = 0;
    
    // 根据关卡设置难度
    if (level === 1) {
        gameState.gameSpeed = 2;
        gameState.obstacleInterval = 1500;
    } else if (level === 2) {
        gameState.gameSpeed = 3;
        gameState.obstacleInterval = 1200;
    } else { // 无尽模式
        gameState.gameSpeed = 4;
        gameState.obstacleInterval = 1000;
    }
    
    levelScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');
    scoreDisplay.textContent = `分数: ${gameState.score}`;
    
    requestAnimationFrame(gameLoop);
}

// 游戏主循环
function gameLoop(timestamp) {
    if (!gameState.isPlaying) return;
    
    update();
    render();
    
    requestAnimationFrame(gameLoop);
}

// 更新游戏状态
function update() {
    // 更新小鸟位置
    gameState.bird.velocity += gameState.bird.gravity;
    gameState.bird.y += gameState.bird.velocity;
    bird.style.top = `${gameState.bird.y}px`;
    
    // 生成障碍物
    const now = Date.now();
    if (now - gameState.lastObstacleTime > gameState.obstacleInterval) {
        createObstacle();
        gameState.lastObstacleTime = now;
    }
    
    // 更新障碍物位置
    gameState.obstacles.forEach(obstacle => {
        obstacle.x -= gameState.gameSpeed;
    });
    
    // 移除屏幕外的障碍物
    gameState.obstacles = gameState.obstacles.filter(obstacle => obstacle.x + 60 > 0);
    
      // 检测碰撞
      if (checkCollision()) {
          if (gameState.currentLevel === 3 && gameState.score > 0 && gameState.score % 1024 === 0) {
              gameOver(true, "哇！你发现了第三关的隐藏通关方法！");
          } else {
              gameOver();
          }
          return;
      }
    
      // 更新分数
      if (gameState.currentLevel < 3) {
          // 关卡模式：分数基于距离
          gameState.score += gameState.gameSpeed;
          if (gameState.currentLevel === 1 && gameState.score >= 1000) {
              if (!gameState.unlockedLevels.includes(2)) {
                  gameState.unlockedLevels.push(2);
              }
              gameOver(true, "恭喜通过第一关！");
              return;
          } else if (gameState.currentLevel === 2 && gameState.score >= 2000) {
              if (!gameState.unlockedLevels.includes(3)) {
                  gameState.unlockedLevels.push(3);
              }
              gameOver(true, "恭喜通过第二关！");
              return;
          }
      } else if (gameState.currentLevel === 3) {
          // 第三关无尽模式，不自动通关
          gameState.score += 1;
    } else {
        // 无尽模式：分数基于存活时间
        gameState.score += 1;
    }
    scoreDisplay.textContent = `分数: ${gameState.score}`;
}

// 渲染游戏
function render() {
    // 清除旧的障碍物
    document.querySelectorAll('.obstacle').forEach(el => el.remove());
    
    // 渲染障碍物
    gameState.obstacles.forEach(obstacle => {
        const obstacleElement = document.createElement('div');
        obstacleElement.className = 'obstacle';
        obstacleElement.style.left = `${obstacle.x}px`;
        obstacleElement.style.top = `${obstacle.top}px`;
        obstacleElement.style.height = `${obstacle.height}px`;
        obstacleElement.style.width = '60px';
        obstacleElement.style.backgroundColor = 'green';
        obstacleElement.style.position = 'absolute';
        gameScreen.appendChild(obstacleElement);
    });
}

// 创建障碍物
function createObstacle() {
    const minGap = gameState.currentLevel === 3 ? 150 : 200;
    const maxGap = gameState.currentLevel === 3 ? 250 : 300;
    const gap = Math.random() * (maxGap - minGap) + minGap;
    const topHeight = Math.random() * (400 - gap);
    
    gameState.obstacles.push({
        x: 400,
        top: 0,
        height: topHeight,
        gap: gap
    });
    
    gameState.obstacles.push({
        x: 400,
        top: topHeight + gap,
        height: 600 - (topHeight + gap),
        gap: gap
    });
}

// 检测碰撞
function checkCollision() {
    // 检测边界碰撞
    if (gameState.bird.y < 0 || gameState.bird.y > 600 - 30) {
        return true;
    }
    
    // 检测障碍物碰撞
    const birdRect = {
        x: 50,
        y: gameState.bird.y,
        width: 40,
        height: 30
    };
    
    for (const obstacle of gameState.obstacles) {
        const obstacleRect = {
            x: obstacle.x,
            y: obstacle.top,
            width: 60,
            height: obstacle.height
        };
        
        if (isColliding(birdRect, obstacleRect)) {
            return true;
        }
    }
    
    return false;
}

// 碰撞检测辅助函数
function isColliding(rect1, rect2) {
    return rect1.x < rect2.x + rect2.width &&
           rect1.x + rect1.width > rect2.x &&
           rect1.y < rect2.y + rect2.height &&
           rect1.y + rect1.height > rect2.y;
}

// 跳跃
function jump() {
    if (gameState.isPlaying) {
        gameState.bird.velocity = gameState.bird.jumpForce;
    }
}

  // 游戏结束
  function gameOver(win = false, message = '') {
      gameState.isPlaying = false;
      gameScreen.classList.add('hidden');
      gameOverScreen.classList.remove('hidden');
      finalScoreDisplay.textContent = `最终分数: ${gameState.score}`;
      
      if (win) {
          document.querySelector('#game-over-screen h2').textContent = message || '关卡完成！';
      } else {
          document.querySelector('#game-over-screen h2').textContent = '游戏结束';
      }
  }

// 重新开始游戏
function restartGame() {
    gameOverScreen.classList.add('hidden');
    showLevelScreen();
}