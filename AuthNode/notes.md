 To configure JWT authentication in EMQX to handle different ACLs per client, you configure the JWT authenticator once on the broker, and your authentication server issues different JWT tokens with different `acl` claims for each client.

## EMQX JWT Configuration

Configure JWT authentication in EMQX Dashboard:

1. Navigate to **Access Control** → **Authentication**
2. Click **Create** and select **JWT** as the mechanism
3. Configure these key settings:

**JWT From**: Choose where the token is located - `password` or `username` field [(1)](https://docs.emqx.com/en/cloud/latest/deployments/jwt_auth.html#how-jwt-authentication-works)  [(2)](https://docs.emqx.com/en/emqx/latest/access-control/authn/jwt.html) 

**Algorithm**: Select your encryption method:
- `hmac-based` (HS256, HS384, HS512) - uses symmetric keys
- `public-key` (RS256, RS384, RS512, ES256, ES384, ES512) - uses public/private key pairs**For HMAC-based**:
- **Secret**: The key used to verify the signature [(1)](https://docs.emqx.com/en/cloud/latest/deployments/jwt_auth.html#how-jwt-authentication-works) 
- **Secret Base64 Encode**: Whether EMQX should decode the secret using Base64**For Public-key**:
- **Public Key**: The PEM-formatted public key for signature verification**Payload**: Add custom claims checks if needed (optional - the `acl` claim is processed automatically)## How Different ACLs Work

The key point is: **you don't configure different ACLs in EMQX** - you configure JWT authentication once, and your authentication server generates different JWT tokens with different `acl` claims for each client or client type. [(2)](https://docs.emqx.com/en/emqx/latest/access-control/authn/jwt.html) 

Each client receives a unique JWT from your authentication server containing:
- Standard claims (`exp`, `iat`, `nbf`)
- Identity information (`username`, `clientid`)
- **Client-specific ACL rules in the `acl` claim**

## Example Workflow

1. **Client requests token from your auth server**
2. **Your auth server determines the client's permissions** and generates a JWT:

```json
{
  "username": "sensor_device_001",
  "exp": 1719830400,
  "acl": [
    {
      "permission": "allow",
      "action": "publish",
      "topic": "sensors/${clientid}/data"
    },
    {
      "permission": "allow",
      "action": "subscribe",
      "topic": "sensors/${clientid}/commands"
    },
    {
      "permission": "deny",
      "action": "all",
      "topic": "#"
    }
  ]
}
```

3. **Client connects to EMQX** with this JWT in the password/username field
4. **EMQX verifies the signature** and extracts the ACL rules
5. **The extracted ACL rules apply only to that specific client** [(3)](https://docs.emqx.com/en/emqx/latest/access-control/authn/acl.html)  [(2)](https://docs.emqx.com/en/emqx/latest/access-control/authn/jwt.html) 

## Important Notes

- Each JWT is for **one client** - the ACL rules in that token apply only to the client using that token [(2)](https://docs.emqx.com/en/emqx/latest/access-control/authn/jwt.html) 
- JWT ACL rules are checked **before all other Authorizers** [(3)](https://docs.emqx.com/en/emqx/latest/access-control/authn/acl.html) 
- You can use placeholders like `${clientid}` and `${username}` in topic patterns, which get replaced at runtime [(3)](https://docs.emqx.com/en/emqx/latest/access-control/authn/acl.html)  [(2)](https://docs.emqx.com/en/emqx/latest/access-control/authn/jwt.html) 
- The `acl` claim is automatically processed - you don't need to configure it in the "Payload" section of JWT settings [(1)](https://docs.emqx.com/en/cloud/latest/deployments/jwt_auth.html#how-jwt-authentication-works) 

**SOURCES USED:** ,  [(3)](https://docs.emqx.com/en/emqx/latest/access-control/authn/acl.html) ,  [(2)](https://docs.emqx.com/en/emqx/latest/access-control/authn/jwt.html) 