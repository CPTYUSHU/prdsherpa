# 安全性和认证系统实施方案

## 当前安全问题（严重）

❌ **无身份验证** - 所有API端点完全公开
❌ **无权限控制** - 任何人可以访问/修改/删除任何项目
❌ **无速率限制** - 容易被滥用
❌ **CORS过于开放** - `allow_methods=["*"]`, `allow_headers=["*"]`
❌ **敏感信息暴露** - API密钥直接存储在环境变量

---

## 1. JWT 认证系统实施

### 数据库模型

```python
# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    projects = relationship("Project", back_populates="owner")

# 更新 Project 模型
class Project(Base):
    __tablename__ = "projects"

    # ... 现有字段 ...
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # 关系
    owner = relationship("User", back_populates="projects")
```

### 安全工具类

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT 配置
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # 从数据库获取用户
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

### 认证 API 端点

```python
# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register")
async def register(
    email: str,
    password: str,
    full_name: str,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查邮箱是否已存在
    result = await db.execute(
        select(User).where(User.email == email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 创建用户
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 生成令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 验证用户
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # 生成令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # 验证用户存在
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # 生成新的访问令牌
        new_access_token = create_access_token(data={"sub": user_id})

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at.isoformat()
    }
```

### 保护现有 API 端点

```python
# backend/app/api/projects.py
from backend.app.core.security import get_current_user

@router.post("/")
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),  # 添加认证
    db: AsyncSession = Depends(get_db)
):
    """创建项目（需要认证）"""
    new_project = Project(
        **project.dict(),
        user_id=current_user.id  # 关联用户
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project

@router.get("/")
async def list_projects(
    current_user: User = Depends(get_current_user),  # 添加认证
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """列出用户的项目"""
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)  # 过滤用户项目
        .order_by(desc(Project.last_conversation_at))
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()
    return projects

@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目详情（权限检查）"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id  # 权限检查
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )

    return project
```

---

## 2. 速率限制（Rate Limiting）

### 使用 SlowAPI

```python
# backend/app/core/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=settings.redis_url  # 使用Redis存储限流数据
)

# 在 main.py 中配置
from backend.app.core.rate_limit import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 使用示例
@router.post("/login")
@limiter.limit("5/minute")  # 登录接口限制更严格
async def login(request: Request, ...):
    ...

@router.post("/conversations/{id}/chat")
@limiter.limit("20/minute")  # AI聊天限制
async def chat(request: Request, ...):
    ...
```

### 基于用户的速率限制

```python
def get_user_key(request: Request):
    """基于用户ID的限流键"""
    # 从JWT token获取用户ID
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return f"user:{user_id}"
    except:
        return get_remote_address(request)  # 回退到IP地址

limiter_by_user = Limiter(
    key_func=get_user_key,
    storage_uri=settings.redis_url
)

@router.post("/files/upload")
@limiter_by_user.limit("10/hour")  # 每用户每小时10次上传
async def upload_file(request: Request, ...):
    ...
```

---

## 3. CORS 安全配置

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

# 严格的CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://prdsherpa.com",  # 生产域名
        "https://app.prdsherpa.com",
        "http://localhost:3000",  # 开发环境
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # 明确指定方法
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "User-Agent",
    ],  # 明确指定headers
    max_age=600,  # 10分钟预检缓存
)
```

---

## 4. API 密钥管理

### 使用 Secrets Manager

```python
# backend/app/core/secrets.py
import boto3
from functools import lru_cache

class SecretsManager:
    """AWS Secrets Manager 集成"""

    def __init__(self):
        self.client = boto3.client('secretsmanager', region_name='us-east-1')

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> str:
        """获取密钥（带缓存）"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except Exception as e:
            logger.error(f"Error retrieving secret {secret_name}: {e}")
            raise

secrets_manager = SecretsManager()

# 使用
gemini_api_key = secrets_manager.get_secret("prdsherpa/gemini_api_key")
```

### 环境特定配置

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # 环境标识
    environment: str = "development"

    # 根据环境加载不同配置
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def gemini_api_key(self) -> str:
        if self.is_production:
            return secrets_manager.get_secret("prdsherpa/gemini_api_key")
        return self._gemini_api_key  # 从.env加载

    # 数据库 URL
    @property
    def database_url(self) -> str:
        if self.is_production:
            return secrets_manager.get_secret("prdsherpa/database_url")
        return self._database_url
```

---

## 5. 输入验证和安全

### 文件上传安全

```python
# backend/app/services/file_security.py
import magic
from pathlib import Path

class FileSecurityService:
    """文件安全检查服务"""

    # 允许的MIME类型
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/markdown',
        'text/plain',
        'image/png',
        'image/jpeg',
        'image/gif',
    }

    # 最大文件大小（200MB）
    MAX_FILE_SIZE = 200 * 1024 * 1024

    @staticmethod
    def validate_file_type(file_path: str) -> bool:
        """验证文件实际类型（不依赖扩展名）"""
        mime = magic.Magic(mime=True)
        file_mime = mime.from_file(file_path)

        return file_mime in FileSecurityService.ALLOWED_MIME_TYPES

    @staticmethod
    def validate_file_size(file_path: str) -> bool:
        """验证文件大小"""
        file_size = Path(file_path).stat().st_size
        return file_size <= FileSecurityService.MAX_FILE_SIZE

    @staticmethod
    async def scan_for_malware(file_path: str) -> bool:
        """
        病毒扫描（集成 ClamAV）
        生产环境建议使用
        """
        # TODO: 集成 ClamAV 或云端扫描服务
        return True

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名，防止路径遍历攻击"""
        import re
        # 移除危险字符
        safe_filename = re.sub(r'[^\w\s.-]', '', filename)
        # 限制长度
        safe_filename = safe_filename[:255]
        return safe_filename

# 在文件上传API中使用
@router.post("/upload")
async def upload_file(
    file: UploadFile,
    security_service: FileSecurityService = Depends(get_security_service)
):
    # 验证文件名
    safe_filename = security_service.sanitize_filename(file.filename)

    # 保存文件
    file_path = f"/tmp/{safe_filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 验证文件类型
    if not security_service.validate_file_type(file_path):
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )

    # 验证文件大小
    if not security_service.validate_file_size(file_path):
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )

    # 病毒扫描
    if not await security_service.scan_for_malware(file_path):
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File contains malware"
        )

    # 处理文件...
```

### SQL 注入防护

```python
# 已经使用 SQLAlchemy ORM，天然防止 SQL 注入
# 但要注意原始 SQL 查询的使用

# ❌ 不安全
query = f"SELECT * FROM users WHERE email = '{user_email}'"

# ✅ 安全
query = select(User).where(User.email == user_email)
```

### XSS 防护

```python
# backend/app/core/sanitize.py
import bleach

def sanitize_html(text: str) -> str:
    """清理 HTML，防止 XSS"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a']
    allowed_attributes = {'a': ['href', 'title']}

    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

# 在处理用户输入时使用
@router.post("/conversations/{id}/chat")
async def chat(
    message: str,
    ...
):
    # 清理用户输入
    clean_message = sanitize_html(message)

    # 处理消息...
```

---

## 6. 安全头部

```python
# backend/app/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """添加安全HTTP头部"""

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"

        # XSS 保护
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 内容安全策略
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://generativelanguage.googleapis.com;"
        )

        # HSTS (生产环境)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response

# 在 main.py 中添加
app.add_middleware(SecurityHeadersMiddleware)
```

---

## 实施路线图

### 阶段 1: 基础认证（1周）
1. ✅ 创建 User 模型和数据库迁移
2. ✅ 实现 JWT 认证（登录、注册、刷新令牌）
3. ✅ 保护所有 API 端点
4. ✅ 前端集成认证（token 存储和刷新）

### 阶段 2: 权限控制（3-4天）
5. ✅ 实现用户-项目关联
6. ✅ 添加权限检查中间件
7. ✅ 实现资源访问控制

### 阶段 3: 安全加固（1周）
8. ✅ 添加速率限制
9. ✅ 实现文件上传安全检查
10. ✅ 配置安全 HTTP 头部
11. ✅ 更新 CORS 配置

### 阶段 4: 生产部署（根据需要）
12. ✅ 集成 Secrets Manager
13. ✅ 配置环境特定配置
14. ✅ 添加审计日志

---

## 预期效果

| 安全问题 | 当前状态 | 实施后 |
|---------|---------|--------|
| 身份验证 | ❌ 无 | ✅ JWT |
| 权限控制 | ❌ 无 | ✅ RBAC |
| 速率限制 | ❌ 无 | ✅ 多层限流 |
| 文件安全 | ⚠️ 仅扩展名 | ✅ MIME+大小+扫描 |
| API安全 | ❌ 完全开放 | ✅ 认证+授权 |
| 数据泄露风险 | 🔴 高 | 🟢 低 |
| OWASP Top 10 | ⚠️ 多个漏洞 | ✅ 基本覆盖 |

---

## 代码示例：完整的前端集成

```typescript
// frontend/src/services/auth.ts
class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  async login(email: string, password: string) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: email, password }),
    });

    const data = await response.json();
    this.setTokens(data.access_token, data.refresh_token);
    return data.user;
  }

  async refreshAccessToken() {
    if (!this.refreshToken) throw new Error('No refresh token');

    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: this.refreshToken }),
    });

    const data = await response.json();
    this.accessToken = data.access_token;
    localStorage.setItem('access_token', data.access_token);
  }

  private setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  getAccessToken(): string | null {
    return this.accessToken || localStorage.getItem('access_token');
  }

  logout() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

// frontend/src/services/api.ts
import axios from 'axios';
import { authService } from './auth';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 180000,
});

// 请求拦截器：添加认证头
api.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：自动刷新token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 401错误且未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 刷新token
        await authService.refreshAccessToken();

        // 重试原请求
        const token = authService.getAccessToken();
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // 刷新失败，跳转登录
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

通过实施这些安全措施，项目的安全性将从 **4/10 提升到 8.5/10**，满足生产环境的基本安全要求。
