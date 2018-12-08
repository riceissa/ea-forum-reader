This post is a tutorial on using GraphQL to query for information about
LessWrong and the Effective Altruism Forum. It's mostly intended for people who
have wanted to explore LW/EA Forum data but have found GraphQL intimidating
(this was the case for myself until several weeks ago).

# General steps for writing a query

(This section will make more sense if you have seen some example queries; see
next section.)

For the queries that I know how to do, here is the general outline of steps:

1. Go to <https://www.lesswrong.com/graphiql> or
   <https://forum.effectivealtruism.org/graphiql> depending on which forum you
   want to query data for.

2. Figure out what the output type should be (e.g. `comments`, `comment`,
   `posts`, `post`).

3. Type `{output_type(input)}` into GraphiQL and hover over `input`.

   Here is what it looks like for the `comment` output type:

   [![](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comment-input-hover.png)](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comment-input-hover.png)

   Here is what it looks like for the `comments` output type:

   [![](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comments-input-hover.png)](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comments-input-hover.png)

4. Click
   on the type that appears after `input` (e.g. `MultiCommentInput`, `SingleCommentInput`).
   A column on the right should appear (if it was not there already).
   Depending on the fields listed in that column, there will now be two ways to proceed.
   (Generally, it seems like singular output types (e.g. `comment`) will have
   `selector` and plural output types (e.g. `comments`) will have `terms`.)

   Here is what it looks like for the `comment` output type. In the image, I have
   already clicked on `SingleCommentInput` so you can see `selector` under the
   documentation (rightmost) column.

   [![](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comment-SingleCommentInput.png)](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comment-SingleCommentInput.png)

   Here is what it looks like for the `comments` output type. Again, in this image,
   I have already clicked on `MultiCommentInput` so you can see `terms` under the
   documentation (rightmost) column.

   [![](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comments-MultiCommentInput.png)](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comments-MultiCommentInput.png)


   In the fields listed, if there is `selector` (e.g. for `comment`):

   - Click on the selector type (e.g. `CommentSelectorUniqueInput`). Use one of
     the fields (e.g. `_id`) to pick out the specific item you want.

     Here is what you should click on:

     [![](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comment-CommentSelectorUniqueInput.png)](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comment-CommentSelectorUniqueInput.png)

     What it looks like after you have clicked:

     [![](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comment-fields.png)](https://raw.githubusercontent.com/riceissa/ea-forum-reader/master/tutorial/comment-fields.png)

   If there is `terms` (e.g. `comments`):

   - Go to the
     [collections](https://github.com/LessWrong2/Lesswrong2/tree/devel/packages/lesswrong/lib/collections)
     directory in the LessWrong 2.0 codebase, and find the `views.js` file for
     your output type. For example, if your output type is `comments`, then the
     corresponding `views.js` file is located at
     [`collections/comments/views.js`](https://github.com/LessWrong2/Lesswrong2/blob/devel/packages/lesswrong/lib/collections/comments/views.js).

   - Look through the various "views" in the `views.js` file to see if there is
     a relevant view. (There is also a default view if you don't select any
     view.) The main things to pay attention to are the `selector` block (which
     controls how the results will be filtered) and the `options` block (which
     mainly controls how the results are sorted).

   - Pass in parameters for that view using keys in the `terms` block.

5. Start a `results` block, and select the fields you want to see for this output type.
   (If you don't select any fields, it will default to all fields, so you can
   do that once and delete the fields you don't need.)

# Examples

I've built a sample interface for both LessWrong and EA Forum that allows an
easy way to access the queries used to generate pages:

- <https://lw2.issarice.com/>
- <https://eaforum.issarice.com/>

By passing `format=queries` in the URL to any page, you can view the GraphQL
queries that were made to generate that page. Rather than showing many examples
in this post, I will just show one example in this post, and let you explore
the reader.

As an example, consider the page
<https://eaforum.issarice.com/?view=top>.
Clicking on "Queries" at the top of the page takes you to the page
<https://eaforum.issarice.com/?view=top&offset=0&before=&after=&format=queries>
Here you will see the following:

```
    {
      posts(input: {
        terms: {
          view: "top"
          limit: 50
          meta: null  # this seems to get both meta and non-meta posts



        }
      }) {
        results {
          _id
          title
          slug
          pageUrl
          postedAt
          baseScore
          voteCount
          commentsCount
          meta
          question
          url
          user {
            username
            slug
          }
        }
      }
    }

Run this query



    {
      comments(input: {
        terms: {
          view: "recentComments"
          limit: 10
        }
      }) {
        results {
          _id
          post {
            _id
            title
            slug
          }
          user {
            _id
            slug
          }
          plaintextExcerpt
          htmlHighlight
          postId
          pageUrl
        }
      }
    }

Run this query
```

Clicking on "Run this query" (not linked in this tutorial, but linked in the
actual page) below each query will take you to the GraphiQL page with the query
preloaded. There, you can click on the "Execute Query" button (which looks like
a play button) to actually run the query and see the result.

I should note that my reader implementation is optimized for my own (probably
unusual) consumption and learning. For article-reading and commenting purposes
(i.e. not for learning how to use GraphQL), most users will probably prefer to
use the official versions of the forums or the GreaterWrong counterparts.

# Tips

- In GraphiQL, hovering over some words like `input` and `results` and then
  clicking on the resulting tooltip will show the parameters that can be passed
  to that block.
- Forum search is *not* done via GraphQL. Rather, a separate API (the Algolia
  search API) is used. Use of the search API is outside the scope of this
  tutorial. This is also why the search results page on my reader
  ([example](https://eaforum.issarice.com/search.php?q=hpmor)) has no "Queries"
  link ([for now](https://github.com/riceissa/ea-forum-reader/issues/8)).
- For queries that use a `terms` block: even though a "view" is just a
  [shorthand](http://docs.vulcanjs.org/terms-parameters.html) for a
  selector/options pair, it is not possible to pass in arbitrary
  selector/options pairs (due to the way security is handled by Vulcan).
  If you don't use a view, the default view is selected.
  The main consequence of this is that you won't be able to make some queries
  that you might want to make.
- Some queries are hard/impossible to do. Examples: (1) getting comments of a
  user by placing conditions on the parent comment or post (e.g. finding all
  comments by user 1 where they are replying to user 2); (2) querying and
  sorting posts by a function of arbitrary fields (e.g. as a function of
  `baseScore` and `voteCount`); (3) finding the highest-karma users looking
  only at the past $N$ days of activity.
- GraphQL vs GraphiQL: `/graphiql` seems to be the endpoint for the interactive
  explorer for GraphQL, whereas `/graphql` is the endpoint for the actual API.
  So when you are actually querying the API (via a program you write) I think
  you want to be using <https://www.lesswrong.com/graphql> and
  <https://forum.effectivealtruism.org/graphql> (or at least, that is what I am
  doing and it works).

# Acknowledgments

Thanks to:

- Louis Francini for helping me with some GraphQL queries and for feedback on
  the post and the reader.
- Oliver Habryka for answering some questions I had about GraphQL.
- Vipul Naik for funding my work on this post and some of my work on the
  reader.
