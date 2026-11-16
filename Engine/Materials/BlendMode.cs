namespace Engine.Materials;

// How the color of a material is combined with the color already in the framebuffer.
public enum BlendMode
{
    // No blending: the fragment replaces the color in the framebuffer (and writes the depth).
    Opaque,

    // Transparency: final color = alpha * fragment color + (1 - alpha) * framebuffer color
    // (GL.BlendFunc(BlendingFactor.SrcAlpha, BlendingFactor.OneMinusSrcAlpha)).
    // The drawing order matters: transparent objects are drawn from back to front.
    AlphaBlend,

    // Additive: final color = fragment color + framebuffer color
    // (GL.BlendFunc(BlendingFactor.One, BlendingFactor.One)), e.g. for fire or magic particles.
    // The drawing order does not matter.
    Additive
}
