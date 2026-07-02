export async function GET() {
  try {
    const res = await fetch(`${process.env.AZL_BASE_URL}/chronicle`, { 
      headers: { 'X-AZL-Key': process.env.AZL_SECRET_KEY },
      cache: 'no-store'
    });
    return Response.json(await res.json());
  } catch (e) {
    return Response.json({ 
      error: "Chronicle offline", 
      law: "N×0=N", 
      pulses: [] 
    });
  }
}
