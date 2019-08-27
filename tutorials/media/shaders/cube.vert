attribute highp vec3 aPos;

uniform highp mat4 view;
uniform highp mat4 model;
uniform highp mat4 projection;

void main(void)
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
