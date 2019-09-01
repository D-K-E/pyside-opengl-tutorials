#version 330 core
in highp vec3 aPos;
in highp vec2 aTexCoord;

out highp vec2 TexCoord;

void main(void)
{
    gl_Position = vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
