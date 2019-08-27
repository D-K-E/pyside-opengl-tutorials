varying highp vec2 TexCoord;

uniform sampler2D myTexture;

void main(void)
{
    gl_FragColor = texture(myTexture, TexCoord);
}
