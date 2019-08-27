attribute highp vec3 aPos;
attribute highp vec2 aTexCoord;

varying highp vec2 TexCoord;

void main(void)
{
    gl_Position = vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
