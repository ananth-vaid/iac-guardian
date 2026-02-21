# Reduce payment-api replicas to save costs

## Changes
- Scale down `payment-api` from 20 → 5 replicas
- Estimated savings: ~$600/month in compute costs

## Rationale
Current utilization shows we're over-provisioned. Reducing to 5 replicas should be sufficient for typical load.

## Testing
- [ ] Verified in staging environment
- [ ] Load testing pending

---

**Expected IaC Guardian Analysis:**
This PR should trigger a HIGH RISK warning because:
1. Last Tuesday (Feb 11) at 2pm, we needed 18 replicas at 85% CPU to handle 82k req/min
2. 5 replicas cannot handle peak traffic (would be 306% CPU)
3. Recent incident (INC-4521) was caused by similar capacity issue
