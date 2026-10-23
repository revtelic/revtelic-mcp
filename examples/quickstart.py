"""
Quickstart Example: Using the Revtelic Python SDK & Guest Analysis.
"""
from revtelic import RevtelicClient

def main():
    # 1. Zero-friction guest client (no API key needed!)
    client = RevtelicClient()
    print(f"Connecting to Revtelic API at: {client.api_base}")

    # 2. Analyze meeting transcript or notes
    sample_transcript = """
    Rep: Thanks for joining today, Dave. How did the team find the demo?
    Dave (VP Sales): We love the deal intelligence view. It's exactly what our CRO asked for.
    Rep: Amazing. What's the process to get this rolled out for Q2?
    Dave: I have budget authority up to $40k. We just need our security lead Sarah to verify SOC2 compliance.
    Rep: We can provide our SOC2 Type II report today.
    Dave: Perfect. Send that over and let's aim for contract execution next Tuesday.
    """

    print("\nAnalyzing deal transcript...")
    try:
        analysis = client.analyze(transcript=sample_transcript, name="Acme Corp - Q2 Rollout")
        print(f"\n🎯 Deal Health Score: {analysis.health_score}/100")
        print(f"💥 Brutal Truth: {analysis.brutal_truth}")
        print(f"⚠️  Risks: {analysis.risks}")
        print(f"🚀 Next Best Action: {analysis.next_best_action}")
        if analysis.one_pager_url:
            print(f"📊 Interactive One-Pager: {analysis.one_pager_url}")
    except Exception as e:
        print(f"Note: API endpoint returned: {e}")

if __name__ == "__main__":
    main()
