# 🔧 Migration Plan: From Service-Level Security to Zero-Trust Hybrid Authentication

## Executive Summary

This document outlines a comprehensive plan for migrating from a decentralized service-level security model to a **zero-trust hybrid authentication architecture** using an API Gateway. The new model eliminates duplicated authentication logic while maintaining strong security through local JWT validation.

The migration will:
- ✅ Enhance system security via zero-trust principles
- ✅ Improve performance by reducing redundant calls to Auth Service
- ✅ Reduce maintenance overhead
- ✅ Align with cloud-native and microservices best practices

All changes are implemented in phases to ensure zero downtime and full rollback capability.

---

## Current State Analysis

### Service-Level Security Model

Currently, each microservice implements its own authentication:

```
Client → Product Service (validates JWT with Firebase Admin SDK)
Client → Cart Service (validates JWT with Firebase Admin SDK)
Client → Auth Service (issues tokens)
```

#### Key Characteristics:
- Direct client communication with individual services
- Each service independently validates JWTs using Firebase Admin SDK
- No centralized authentication layer
- Multiple services hold private keys or admin privileges

#### Identified Issues

| Issue | Risk |
|------|------|
| **Duplicated Authentication Logic** | Every service reimplements auth; prone to drift |
| **Inconsistent Security Standards** | One misconfigured service compromises all |
| **Maintenance Overhead** | Security patches require N deploys |
| **High Load on Auth Service** | Frequent token introspection increases latency |
| **Security Anti-Pattern** | Services trust gateway-injected user headers without verification |

---

## Target State: Zero-Trust Hybrid Authentication

### Architecture Overview

```
Client/Browser
     ↓
[API Gateway] ← Validates JWT at edge
     ↓
→ [Auth Service]        (Token issuance only)
→ [Product Service]     (Re-validates token locally)
→ [Cart Service]        (Re-validates token locally)
```

### Key Components

| Component | Role |
|--------|------|
| **API Gateway** | Centralized routing, initial JWT validation, header enrichment |
| **Auth Service** | Single source of truth for login, token issuance, role lookup |
| **Product/Cart Services** | Focus on business logic; re-validate JWTs locally using public key |
| **JWKS Endpoint** | Exposes public keys for RS256 signature verification (`/.well-known/jwks.json`) |

> 🔐 This is **not** a pure "gateway-only" model — it's **zero-trust**: every service verifies identity independently.

---

## Migration Phases

### Phase 1: API Gateway Implementation (Weeks 1–2)

#### Objectives
- Deploy API Gateway as entry point
- Implement secure JWT validation using public-key cryptography
- Route traffic to backend services

#### Tasks

##### Gateway Setup
- Configure routing rules:  
  `/auth/*` → Auth Service  
  `/api/products/*` → Product Service  
  `/api/cart/*` → Cart Service
- Implement **JWT validation middleware** using RS256 + cached JWKS
- Set up rate limiting, CORS, and security headers (HSTS, CSP)
- Enable request tracing with `X-Request-ID`

##### Service Registration
- Register all services in service discovery (e.g., Consul or static config)
- Configure health checks for auto-failover
- Enable logging and monitoring per route

##### Authentication Integration
- Integrate with Firebase or custom Auth Service
- Use **public-key validation**, not HTTP calls to verify tokens
- Cache JWKS (`https://auth.example.com/.well-known/jwks.json`) with 1-hour TTL
- Forward **original `Authorization` header** + trusted metadata

✅ Example Headers Forwarded:
```http
Authorization: Bearer <original_jwt>
X-Auth-Source: gateway
X-Request-ID: abc123
```

🚫 Never inject `X-User-ID` or `X-Role` unless used as *optimization* (not for auth decisions).

---

### Phase 2: Service Refactoring (Weeks 3–4)

#### Objectives
- Remove duplicated Firebase Admin SDK usage
- Shift to local JWT re-validation
- Prepare for gateway-first flow

#### Tasks

##### Auth Service
- ✅ Keep existing endpoints: `/login`, `/verify-token`
- ✅ Add JWKS endpoint: `GET /.well-known/jwks.json`
- ❌ Do **not remove** direct client access — needed for mobile apps, scripts, integrations
- Add `/roles/{uid}` endpoint for role lookups (used sparingly)

##### Product Service
- Remove `firebase-admin` dependency
- Add local JWT validation using **shared public key**
- Update security middleware to re-validate token
- Accept original `Authorization` header — do **not** trust `X-User-ID`

```python
# app/core/security.py
def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or "Bearer " not in auth:
        raise HTTPException(401, "Not authenticated")

    token = auth.split(" ")[1]
    try:
        # Re-validate using public key (same as gateway)
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        return {
            "uid": payload["sub"],
            "role": payload.get("role", "user")
        }
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
```

##### Cart Service
- Same as Product Service: remove Firebase SDK, add local validation
- For sensitive actions (e.g., apply promo code), optionally call Auth Service to confirm role
- Maintain backward compatibility during transition

---

### Phase 3: Hybrid Transition (Weeks 5–6)

#### Objectives
- Support both legacy (direct) and new (gateway) flows
- Gradually migrate clients
- Validate security and performance

#### Tasks

##### Dual Authentication Support
Services accept two modes:
1. **Gateway Mode**: Token validated at edge → service re-validates locally
2. **Legacy Mode**: Direct call → service validates directly (temporary)

Detect mode:
```python
if request.headers.get("X-Gateway") == "true":
    # Use optimized path (still re-validate!)
else:
    # Fallback to direct validation
```

But always validate JWT — never skip based on source.

##### Client Migration
- Update frontend to use gateway URLs
- Redirect API traffic through gateway via DNS or load balancer
- Monitor traffic split: % via gateway vs direct
- Log any attempts to bypass gateway

##### Testing and Validation
- End-to-end testing of authentication flow
- Performance benchmarking (latency, RPS)
- Security validation including spoofing attempts

---

### Phase 4: Full Migration and Optimization (Weeks 7–8)

#### Objectives
- Complete transition to gateway-based routing
- Optimize performance
- Harden security
- Remove legacy code

#### Tasks

##### Complete Migration
- Deprecate direct access to non-auth services via firewall rules
- Allow only Auth Service to be publicly accessible
- Finalize gateway configuration and monitoring

##### Performance Optimization
- Cache JWKS public keys in memory (refresh hourly)
- Use Redis to cache frequent role lookups (short TTL)
- Implement response caching for static content

##### Security Hardening
- Block direct access to internal services via network policies
- Add security headers via gateway:
  ```http
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Strict-Transport-Security: max-age=31536000
  ```
- Rotate signing keys quarterly using `kid` rotation in JWKS

---

## Technical Implementation Details

### API Gateway Configuration

#### Authentication Flow
1. Client logs in → Auth Service issues RS256-signed JWT
2. Client sends request:  
   ```http
   GET /api/products/5
   Authorization: Bearer <token>
   ```
3. API Gateway:
   - Verifies signature using cached JWKS
   - Checks `exp`, `iss`, `aud`
   - Forwards **original token** and metadata
4. Downstream Service:
   - Re-validates JWT using same public key
   - Extracts `sub`, `role`
   - Proceeds with business logic

> 🔁 No HTTP call to Auth Service after login.

#### Token Handling
```python
# In Gateway: validate and forward
payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])

# Forward original Authorization header
headers = {
    "Authorization": f"Bearer {token}",
    "X-Auth-Source": "gateway",
    "X-Request-ID": request_id
}
```

Downstream services **must re-validate** the same token.

---

### Service Modifications

#### Auth Service
```python
@app.get("/.well-known/jwks.json")
async def jwks():
    """Expose public keys for JWT validation."""
    return {"keys": [public_jwk]}

@app.post("/login")
async def login(credentials: LoginRequest):
    token = create_jwt(uid=user.uid, role=user.role)
    return {"token": token}
```

Keep `/login` and JWKS accessible — essential for clients.

---

#### Product Service
```python
# Remove firebase-admin
# Use local JWT validation

PUBLIC_KEY = load_public_key_from_env_or_jwks()

def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or "Bearer " not in auth:
        raise HTTPException(401, "Missing token")

    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        return {"uid": payload["sub"], "role": payload.get("role", "user")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

No more direct Firebase calls.

---

#### Cart Service
Same pattern:
- Re-validate JWT locally
- Only call Auth Service when confirming elevated roles (e.g., admin promo codes)

```python
if user["role"] == "admin":
    full_user = await auth_client.get_user(user["uid"])  # Optional deep check
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Header Spoofing** | Never trust `X-User-*`; always re-validate JWT |
| **Downtime During Migration** | Dual-mode support; feature flags |
| **Performance Degradation** | Cache JWKS; benchmark before/after |
| **Security Gaps** | Penetration testing; automated security scans |
| **Key Compromise** | Use RS256; rotate keys quarterly; store private key securely |

---

## Rollback Strategy

- Maintain legacy authentication code during transition
- Use feature flag: `ENABLE_GATEWAY_AUTH=true/false`
- If issues arise:
  1. Set flag to `false`
  2. Re-enable direct service access
  3. Investigate and fix
- All changes are reversible within minutes

---

## Testing Plan

### Phase 1: Unit & Integration Tests
- Test JWT validation logic in gateway
- Mock JWKS responses
- Validate header forwarding

### Phase 2: End-to-End Testing
- Simulate login → API call flow
- Measure latency reduction
- Verify no Auth Service overload

### Phase 3: Security & Resilience Testing
- Attempt header spoofing attacks
- Simulate Auth Service outage
- Test JWKS cache behavior during network failure
- Run canary deployment with 5% traffic

---

## Success Metrics

### Technical Metrics
| Metric | Target |
|-------|--------|
| Avg. Auth Latency | < 50ms |
| Gateway Uptime | 99.9% |
| Token Validation Success Rate | > 99.5% |
| Auth Service RPS Reduction | > 80% |

### Business Metrics
| Metric | Target |
|-------|--------|
| Code Duplication Eliminated | 100% |
| Time to Deploy Security Patches | Reduced by 70% |
| Developer Time Spent on Auth | Cut in half |

---

## Timeline and Resources

| Duration | 8 weeks |
|--------|--------|
| Team | 2 Backend Devs, 1 DevOps Engineer, 1 QA Engineer |
| Milestones |
| Week 2 | API Gateway live with JWT validation |
| Week 4 | All services refactored, dual-mode ready |
| Week 6 | Clients migrated, hybrid fully tested |
| Week 8 | Legacy paths disabled, optimization complete |

---

## Conclusion

This updated migration plan delivers a **secure, scalable, and maintainable authentication architecture** based on **zero-trust principles**.

It moves beyond simple "gateway-only" models by ensuring:
- ✅ No blind trust in headers
- ✅ Local JWT re-validation in every service
- ✅ Use of public-key cryptography (RS256 + JWKS)
- ✅ Graceful migration with rollback safety

The result is a system that scales efficiently in the cloud, resists attacks, and reduces operational burden — while remaining flexible for future growth.

You can now confidently execute this plan knowing it aligns with how companies like Google, Amazon, and Stripe secure their microservices.

Let me know if you'd like this exported as PDF, GitHub repo template, or Docker setup!