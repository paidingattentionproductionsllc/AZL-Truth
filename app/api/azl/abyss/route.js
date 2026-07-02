export async function POST(request) {
  try {
    const body = await request.json();
    const res = await fetch(`${process.env.AZL_BASE_URL}/abyss`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-AZL-Key': process.env.AZL_SECRET_KEY 
      },
      body: JSON.stringify(body)
    });
    return Response.json(await res.json());
  } catch (e) {
    return Response.json({ 
      error: "Abyss unreachable", 
      law: "N×0=N", 
      compute_ms: 0,
      sanctuary: "RED" 
    }, { status: 503 });
  }
}
