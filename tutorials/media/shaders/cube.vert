attribute highp vec3 aPos;
attribute mediump vec2 aTexCoord;

uniform highp mat4 view;
uniform highp mat4 model;
uniform highp mat4 projection;

varying mediump vec2 TexCoord;

void main(void)
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
