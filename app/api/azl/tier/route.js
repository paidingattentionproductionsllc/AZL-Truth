export async function GET() {
  try {
    const res = await fetch(process.env.AZL_BASE_URL, { 
      cache: 'no-store',
      headers: { 'X-AZL-Key': process.env.AZL_SECRET_KEY }
    });
    return Response.json(await res.json());
  } catch (e) {
    return Response.json({ error:"Not Found", law:"N×0=N", sanctuary:"RED" });
  }
}
