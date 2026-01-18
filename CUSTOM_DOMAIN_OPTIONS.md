# Custom Domain Options for Relay Gateway

Current URL: `http://RelayS-Relay-l3JJbpazTzE3-1513127728.us-east-1.elb.amazonaws.com`

## Option 1: Free DNS Service (100% Free) ⭐ RECOMMENDED

Use a free dynamic DNS provider to create a custom subdomain:

### **DuckDNS** (Easiest & Free Forever)
**Cost:** $0
**URL Example:** `relay.duckdns.org` or `mycompany-relay.duckdns.org`

**Steps:**
1. Go to https://www.duckdns.org
2. Sign in with GitHub/Google
3. Create a subdomain (e.g., `mycompany-relay`)
4. Point it to your ALB DNS name using CNAME
5. Done!

**Pros:**
- ✅ Completely free forever
- ✅ No credit card needed
- ✅ Instant setup (5 minutes)
- ✅ Supports HTTPS with Let's Encrypt

**Cons:**
- ⚠️ Domain is `*.duckdns.org` (not your own domain)
- ⚠️ Less professional looking

### **FreeDNS** (More domain options)
**Cost:** $0
**URL Example:** `relay.mooo.com`, `relay-api.25u.com`, etc.

**Steps:**
1. Go to https://freedns.afraid.org
2. Create free account
3. Choose from 50+ free domains
4. Add CNAME record pointing to your ALB
5. Done!

**Pros:**
- ✅ Free
- ✅ Many domain options
- ✅ More professional-looking domains

**Cons:**
- ⚠️ Some domains look spammy
- ⚠️ Can be taken away if inactive

---

## Option 2: AWS Route 53 with Existing Domain ($0.50/month)

If you already own a domain (like `mycompany.com`), add a subdomain:

**Cost:** ~$0.50/month for Route 53 hosted zone queries
**URL Example:** `relay.mycompany.com` or `api.mycompany.com`

**Steps:**

```bash
# 1. Create hosted zone (if you don't have one)
aws route53 create-hosted-zone \
  --name mycompany.com \
  --caller-reference $(date +%s)

# 2. Add CNAME record
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "relay.mycompany.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [
          {"Value": "RelayS-Relay-l3JJbpazTzE3-1513127728.us-east-1.elb.amazonaws.com"}
        ]
      }
    }]
  }'
```

**Pros:**
- ✅ Professional domain
- ✅ Full control
- ✅ Integrates with AWS
- ✅ Can add SSL certificate easily

**Cons:**
- 💰 ~$0.50/month
- ⚠️ Requires existing domain ($12+/year if buying new)

---

## Option 3: AWS Route 53 Alias (Same as Option 2 but cheaper)

Use Route 53 **Alias** record instead of CNAME (no query charges):

**Cost:** $0 (if under 1 billion queries/month)
**URL Example:** `relay.mycompany.com`

**CDK Code:**
```python
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets

# Add to RelayStack
def _create_dns_record(self):
    hosted_zone = route53.HostedZone.from_lookup(
        self, "HostedZone",
        domain_name="mycompany.com"
    )

    route53.ARecord(
        self, "RelayAliasRecord",
        zone=hosted_zone,
        record_name="relay",
        target=route53.RecordTarget.from_alias(
            targets.LoadBalancerTarget(self.ecs_service.load_balancer)
        )
    )
```

**Pros:**
- ✅ Actually free (no Route 53 query charges)
- ✅ Better than CNAME (works at root domain)
- ✅ Professional

**Cons:**
- ⚠️ Still need to own the domain ($12+/year)

---

## Option 4: Cloudflare Free Plan (Free + Better Performance)

Use Cloudflare as your DNS provider:

**Cost:** $0
**URL Example:** `relay.mycompany.com`
**Bonus:** Free CDN, DDoS protection, caching

**Steps:**
1. Sign up at https://cloudflare.com (free plan)
2. Add your domain (or buy a cheap one)
3. Point nameservers to Cloudflare
4. Add CNAME record: `relay` → `RelayS-Relay-l3JJbpazTzE3...amazonaws.com`
5. Enable SSL/TLS (Full mode)

**Pros:**
- ✅ Free forever
- ✅ Free SSL certificate
- ✅ Free CDN (faster worldwide)
- ✅ DDoS protection
- ✅ Caching & performance optimization

**Cons:**
- ⚠️ Still need to own domain

---

## Option 5: Buy Cheap Domain + Cloudflare ($1-5/year)

Buy a cheap domain and use Cloudflare:

**Cost:** $1-5/year for domain
**URL Example:** `relay-api.xyz` or `mycompany-relay.com`

**Cheap Domain Registrars:**
- **Porkbun:** `.xyz` domains for $1-2/year
- **Namecheap:** `.xyz`, `.online` for $1-5/year
- **Cloudflare:** `.xyz` domains at cost (~$1/year)

**Total Setup:**
1. Buy domain ($1-5/year)
2. Point to Cloudflare DNS (free)
3. Add CNAME to your ALB
4. Enable SSL (free)

**Pros:**
- ✅ Very cheap ($1-5/year)
- ✅ Professional custom domain
- ✅ Free SSL, CDN, protection
- ✅ Full control

**Cons:**
- 💰 Small annual cost

---

## Comparison Table

| Option | Cost | Setup Time | Professional | SSL |
|--------|------|------------|--------------|-----|
| **DuckDNS** | **$0** | **5 min** | ⭐⭐ | ✅ Free |
| **FreeDNS** | $0 | 10 min | ⭐⭐⭐ | ✅ Free |
| **Route 53 (own domain)** | $0.50/mo | 15 min | ⭐⭐⭐⭐⭐ | ✅ ACM Free |
| **Route 53 Alias** | $0 | 20 min | ⭐⭐⭐⭐⭐ | ✅ ACM Free |
| **Cloudflare (own domain)** | $0 | 20 min | ⭐⭐⭐⭐⭐ | ✅ Free |
| **Cheap domain + Cloudflare** | $1-5/yr | 30 min | ⭐⭐⭐⭐⭐ | ✅ Free |

---

## My Recommendation: DuckDNS (For Testing) + Cheap Domain (For Production)

### **For Development/Testing:**
Use **DuckDNS** - completely free, instant setup:
```
Your URL: https://mycompany-relay.duckdns.org
```

### **For Production:**
Buy a cheap `.xyz` domain ($1-2/year) + Cloudflare:
```
Your URL: https://relay-api.xyz  or  https://api.mycompany.xyz
```

---

## Quick Setup: DuckDNS (5 Minutes)

1. **Go to https://www.duckdns.org**

2. **Sign in** (GitHub/Google)

3. **Create subdomain:**
   - Enter: `mycompany-relay`
   - Click "add domain"

4. **Update domain:**
   - In the "current ip" field, clear it
   - Click "update ip" once to get the interface
   - Then manually enter: `RelayS-Relay-l3JJbpazTzE3-1513127728.us-east-1.elb.amazonaws.com`
   - Wait... DuckDNS only supports IP addresses, not CNAMEs

Actually, let me correct this - **DuckDNS only works with IP addresses, not CNAMEs**.

For CNAME support, use **FreeDNS** instead:

1. **Go to https://freedns.afraid.org**
2. **Sign up** (free)
3. **Add a subdomain:**
   - Click "Subdomains" → "Add"
   - Choose a free domain (e.g., mooo.com, hopto.org)
   - Type: `CNAME`
   - Subdomain: `relay`
   - Destination: `RelayS-Relay-l3JJbpazTzE3-1513127728.us-east-1.elb.amazonaws.com`
4. **Done!** Your URL: `relay.mooo.com`

---

## Quick Setup: Add SSL/HTTPS (Free)

Once you have a custom domain, add free SSL:

### Option A: AWS Certificate Manager (ACM)
```bash
# Request certificate
aws acm request-certificate \
  --domain-name relay.mycompany.com \
  --validation-method DNS \
  --region us-east-1

# Validate via DNS (add CNAME record provided by ACM)

# Update ALB to use certificate (via AWS Console or CDK)
```

### Option B: Cloudflare (Automatic)
If using Cloudflare, SSL is automatic and free!

---

## Need Help Choosing?

**Just testing/demo?** → **FreeDNS** (free CNAME support)

**Own a domain already?** → **Route 53 Alias** (free, no queries charged)

**Want professional URL cheap?** → **Buy .xyz domain ($1-2/year) + Cloudflare**

**Want completely free forever?** → **FreeDNS**

Let me know which option you want and I can help you set it up!
