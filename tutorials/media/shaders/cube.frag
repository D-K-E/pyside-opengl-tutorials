varying mediump vec2 TexCoord;

uniform sampler2D myTexture1;
uniform sampler2D myTexture2;

void main(void)
{
    // linear interpolation of first texture with second one
    // 30% indicates the amount of the presence of the second one
    gl_FragColor = mix(texture(myTexture1, TexCoord), texture(myTexture2, TexCoord), 0.4);
    //gl_FragColor = texture(myTexture2, TexCoord);
}
